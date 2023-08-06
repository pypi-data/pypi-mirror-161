""" module:: uds.client
    :platform: Posix
    :synopsis: A class file for Universal Diagnostic Service (UDS) client
    moduleauthor:: Patrick Menschel (menschel.p@posteo.de)
    license:: GPL v3
"""

import datetime

from queue import Queue, Empty
from threading import Thread
from typing import Union, Optional, List, Tuple

from socketcan import CanIsoTpSocket
from uds.common import DiagnosticSession, ResetType, ComType, ComCtrlType, DtcSettingType, CompressionMethod, \
    EncryptionMethod, RoutineControlType, concat_read_data_by_id_request, UdsTimeoutError, \
    concat_security_access_request, concat_request_download_request, concat_request_upload_request, \
    concat_routine_control_request, concat_communication_control_request, concat_request_transfer_exit_request, \
    concat_write_data_by_id_request, concat_ecu_reset_request, concat_tester_present_request, \
    concat_control_dtc_setting_request, concat_transfer_data_request, concat_diagnostic_session_control_request, \
    concat_clear_diagnostic_information_request, parse_response, ServiceId, \
    RequestCorrectlyReceivedButResponsePending, concat_read_dtc_information_request, DtcReportType, DtcStatus, \
    DtcSeverety, DtcReadinessGroup, DtcFunctionalGroup

import logging

LOGGER = logging.getLogger(__name__)


class UdsClient:
    """
    UDS Client class

    depends on socketcan
    therefore runs on linux only
    """

    def __init__(self,
                 socket: CanIsoTpSocket,
                 fixed_timings: Optional[dict] = None,
                 ):
        """
        Constructor

        :param socket: A SocketCAN IsoTp socket.
        :param fixed_timings: A dictionary of timing values. If set auto update of session parameters will be skipped.
        """
        self._s = socket
        self.use_fixed_timings = False
        self.session_parameters = \
            {
                "p2_server_max": 0.5,  # 50ms is correct but unrealistic if a connection has not yet been established.
                "p2*_server_max": 5,
                "s3_client": 2,
            }
        if fixed_timings is not None and isinstance(fixed_timings, dict):
            self.use_fixed_timings = True
            self.session_parameters.update(fixed_timings)
        # p2_server_max = The response time between request sent and first response received 50ms
        # p2*_server_max = The response time between consecutive responses,
        # e.g. after RequestCorrectlyReceivedButResponsePending
        # s3_client = The keep-alive time for a client, e.g. a client sends TesterPresent to keep a session alive.

        self.rx_queue = Queue()
        self.rx_handler = Thread(target=self._handle_rx)
        self.rx_handler.setDaemon(True)
        self.rx_handler.start()

    # basic functionality

    def _handle_rx(self) -> None:
        """
        Puts data from socket into a queue,
        where the requester (main thread) in self.recv()
        :return: Nothing.
        """
        while True:
            self.rx_queue.put(self._s.recv())

    def _send(self, data: bytes) -> int:
        """
        Sends data to the socket.
        :param data: The data to be sent.
        :return: The length of data that was sent.
        """
        return self._s.send(data=data)

    def _recv(self, timeout: int) -> Optional[bytes]:
        """
        Receives data from rx_queue in case it was filled by
        rx_handler.
        The underlying queue mechanism may raise an Empty Exception.
        :param timeout: The timeout to wait for a response.
        :return: Data bytes.
        """
        assert 0 < timeout < 10
        return self.rx_queue.get(timeout=timeout)

    def _on_diagnostic_session_control_response(self,
                                                session_parameters: dict) -> None:
        if self.use_fixed_timings is False:
            session_parameters.pop("response_sid")
            LOGGER.debug("New Session Parameters {0}".format(session_parameters))
            self.session_parameters.update(session_parameters)

    def flush_rx_queue(self):
        if not self.rx_queue.empty():
            LOGGER.debug("flushing rx_queue before sending a new request")
            try:
                while resp_bytes := self.rx_queue.get_nowait():
                    LOGGER.debug("dropping {0}".format(resp_bytes))
            except Empty:
                pass

    def request(self, req: bytes, suppress_response: bool = False) -> Optional[dict]:
        """
        Service request function
        It handles transmission, reception and check if a negative response error should be raised
        :param req: The request as bytes.
        :param suppress_response: Don't wait for a response. Should be set when calling request.
        This is not automatically checked.
        :return: The response as bytes.
        :raises: Subtypes of NegativeResponse, UdsTimeoutError, etc.
        """
        self.flush_rx_queue()
        self._send(req)  # TODO: Technically we have to set socket to blocking while send is not done!
        if len(req) > 20:
            LOGGER.debug("Sent {0} ... {1}".format(req[:10].hex(), req[-10:].hex()))
        else:
            LOGGER.debug("Sent {0}".format(req.hex()))
        if suppress_response:
            return
        ts_request_sent = datetime.datetime.now()
        timeout = self.session_parameters.get("p2_server_max")
        resp_dict = None
        while resp_dict is None:
            try:
                resp_bytes = self._recv(timeout=timeout)
            except Empty:
                break
            else:
                try:
                    resp_dict = parse_response(resp_bytes)
                except RequestCorrectlyReceivedButResponsePending:
                    # wait for the real delayed response
                    timeout = self.session_parameters.get("p2*_server_max")
                    continue
                else:
                    time_for_response = datetime.datetime.now() - ts_request_sent
                    LOGGER.debug("Response received after timedelta {0}".format(time_for_response))

                    LOGGER.debug("Received {0}".format(resp_dict))

                    if req[0] == ServiceId.DiagnosticSessionControl:
                        # we update the server's timing info
                        self._on_diagnostic_session_control_response(resp_dict.copy())
                    return resp_dict

        raise UdsTimeoutError

    # convenience functions for specific services

    def diagnostic_session_control(self,
                                   session: DiagnosticSession = DiagnosticSession.ExtendedDiagnosticSession) -> dict:
        """
        Basic uds service diagnostic session control.
        :param session: The requested diagnostic session.
        :return: The data that was returned.
        """
        return self.request(req=concat_diagnostic_session_control_request(session=session))

    def ecu_reset(self,
                  rtype: ResetType = ResetType.HardReset) -> dict:
        """
        Basic uds service ecu reset.
        :param rtype: The requested ResetType.
        :return: The data that was returned.
        """
        return self.request(req=concat_ecu_reset_request(rtype=rtype))

    def security_access(self,
                        security_level: int,
                        key: Optional[bytes] = None,
                        ) -> dict:
        """
        Basic uds service security access.
        The method is called SEED&KEY and was defined in KWP2000(ISO14230).
        The idea is to have a secret needed to compute a key from a given seed.
        In reality the seed/key is 4 bytes big endian and the seed2key function is a simple function,
        e.g. adding some value, rotating the seed, xor it with a mask value etc.

        Each security level is a tuple of an uneven number to request a seed
        and the next (even) number to post a key.
        :param security_level: The security level. Uneven=SeedRequest, Even=KeyPost
        :param key: The key bytes.
        :return: The data that was returned.
        """

        return self.request(req=concat_security_access_request(security_level=security_level,
                                                               key=key))

    def communication_control(self,
                              ctrl_type: ComCtrlType,
                              com_type: ComType = ComType.NormalCommunicationMessages,
                              node_id: Optional[int] = None,
                              suppress_response: bool = False) -> dict:
        """
        Basic uds service communication control.
        :param ctrl_type: The control type.
        :param com_type: The communication type. The scope of messages.
        :param node_id: The Node identification number. Used with enhanced address info.
        :param suppress_response: Suppress the the positive response.
        :return: The data that was returned.
        """
        return self.request(req=concat_communication_control_request(ctrl_type=ctrl_type,
                                                                     com_type=com_type,
                                                                     node_id=node_id,
                                                                     suppress_response=suppress_response),
                            suppress_response=suppress_response)

    def tester_present(self,
                       suppress_response: bool = False) -> dict:
        """
        Basic uds service tester present.
        :param suppress_response: Suppress the the positive response.
        :return: The data that was returned. Actually nothing except for the response_sid.
        """
        return self.request(req=concat_tester_present_request(suppress_response=suppress_response),
                            suppress_response=suppress_response)

    def control_dtc_setting(self,
                            stype: DtcSettingType,
                            dtcs: Optional[List[int]] = None,
                            suppress_response: bool = False):
        """
        Basic uds service control dtc setting.
        :param stype: The DtcSettingType On or Off
        :param dtcs: A list of dtc numbers in range 0-0xFFFFFF
        :param suppress_response: Suppress the the positive response.
        :return: The data that was returned.
        """
        return self.request(
            req=concat_control_dtc_setting_request(stype=stype, dtcs=dtcs, suppress_response=suppress_response),
            suppress_response=suppress_response)

    def read_data_by_id(self,
                        did: int) -> dict:
        """
        Basic uds service read data by id.
        :param did: The diagnostic identifier to be read.
        :return: The data that was returned.
        """
        return self.request(req=concat_read_data_by_id_request(did=did))

    def write_data_by_id(self,
                         did: int,
                         data: bytes) -> dict:
        """
        Basic uds service write data by id.
        :param did: The diagnostic identifier to be read.
        :param data: The data bytes to be written.
        :return: The data that was returned. Actually nothing except for the response_sid and the did for confirmation.
        """
        return self.request(req=concat_write_data_by_id_request(did=did,
                                                                data=data))

    def request_download(self,
                         addr: int,
                         size: int,
                         compression_method: CompressionMethod = CompressionMethod.NO_COMPRESSION,
                         encryption_method: EncryptionMethod = EncryptionMethod.NO_ENCRYPTION,
                         addr_size_len: Union[str, Tuple[int, int]] = "auto",
                         ) -> dict:
        """
        Basic uds service request download.
        :param addr: The address of the download. Hardcoded to 32bit for now.
        :param size: The size of the download. Hardcoded to 32bit for now.
        :param compression_method: The method of compression.
        :param encryption_method: The method of encryption.
        :param addr_size_len: Byte length used to represent addr and size.
        :return: The data that was returned.
        """
        return self.request(req=concat_request_download_request(addr=addr,
                                                                size=size,
                                                                compression_method=compression_method,
                                                                encryption_method=encryption_method,
                                                                addr_size_len=addr_size_len, ))

    def request_upload(self,
                       addr: int,
                       size: int,
                       compression_method: CompressionMethod = CompressionMethod.NO_COMPRESSION,
                       encryption_method: EncryptionMethod = EncryptionMethod.NO_ENCRYPTION,
                       addr_size_len: Union[str, Tuple[int, int]] = "auto",
                       ) -> dict:
        """
        Basic uds service request upload.
        :param addr: The address of the upload. Hardcoded to 32bit for now.
        :param size: The size of the upload. Hardcoded to 32bit for now.
        :param compression_method: The method of compression.
        :param encryption_method: The method of encryption.
        :param addr_size_len: Byte length used to represent addr and size.
        :return: The data that was returned.
        """
        return self.request(req=concat_request_upload_request(addr=addr,
                                                              size=size,
                                                              compression_method=compression_method,
                                                              encryption_method=encryption_method,
                                                              addr_size_len=addr_size_len, ))

    def transfer_data(self,
                      block_sequence_counter: int,
                      data: bytes,
                      ) -> dict:
        """
        Basic uds service transfer data.
        :param block_sequence_counter: The block counter for this transfer.
        :param data: The data to be transferred.
        :return: The data that was returned.
        """
        return self.request(req=concat_transfer_data_request(block_sequence_counter=block_sequence_counter,
                                                             data=data))

    def request_transfer_exit(self,
                              transfer_request_parameters: Optional[bytes] = None,
                              ) -> dict:
        """
        Basic uds service request transfer exit.
        :param transfer_request_parameters: A never used manufacturer specific value.
        :return: The data that was returned.
        """
        return self.request(
            req=concat_request_transfer_exit_request(transfer_request_parameters=transfer_request_parameters))

    def clear_diagnostic_information(self,
                                     dtc_mask: int,
                                     memory_select: Optional[int] = None,
                                     ) -> dict:
        """
        Basic uds service clear diagnostic information.
        :param dtc_mask: The Dtc Mask. A DTC Mask is a group of dtcs, e.g. 0xFFFF33 is emissions-related systems.
        :param memory_select: An optional byte to select a specific error memory, e.g. a secondary error memory mirror.
        :return: The data that was returned.
        """
        return self.request(
            req=concat_clear_diagnostic_information_request(dtc_mask=dtc_mask,
                                                            memory_select=memory_select))

    def read_dtc_information(self,
                             subfunction: DtcReportType,
                             status_filter: Optional[Union[DtcStatus, DtcSeverety, DtcReadinessGroup]] = None,
                             group_filter: Optional[Union[int, DtcFunctionalGroup]] = None,
                             record_filter: Optional[int] = None,
                             memory_select: Optional[int] = None
                             ) -> dict:
        """
        Basic uds service read dtc information.

        :param subfunction: The subfunction of this service.
        :param status_filter: A bitmask to filter by status flags.
        :param group_filter: The Dtc Mask. A DTC Mask is a group of dtcs, e.g. 0xFFFF33 is emissions-related systems.
        :param record_filter: The Record number / Index in Error Memory.
        :param memory_select: An optional byte to select a specific error memory, e.g. a secondary error memory mirror.
        :return: The data that was returned.
        """
        return self.request(
            req=concat_read_dtc_information_request(subfunction=subfunction,
                                                    status_filter=status_filter,
                                                    group_filter=group_filter,
                                                    record_filter=record_filter,
                                                    memory_select=memory_select))

    def routine_control(self,
                        routine_control_type: RoutineControlType,
                        routine_id: int,
                        data: Optional[bytes] = None
                        ) -> dict:
        """
        Basic uds service routine control.
        :param routine_control_type: The control type, e.g. Start/Stop/Poll.
        :param routine_id: The Routine Id.
        :param data: The (optional) data that the routine consumes.
        :return: The request as bytes.
        """
        return self.request(req=concat_routine_control_request(routine_control_type=routine_control_type,
                                                               routine_id=routine_id,
                                                               data=data))
