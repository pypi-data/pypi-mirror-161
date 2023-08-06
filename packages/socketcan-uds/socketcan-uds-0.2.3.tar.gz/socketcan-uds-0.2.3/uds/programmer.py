""" module:: uds.programmer
    :platform: Posix
    :synopsis: A class file for a uds programmer
    moduleauthor:: Patrick Menschel (menschel.p@posteo.de)
    license:: GPL v3
"""
import os
import threading
import time
from abc import ABC, abstractmethod
from collections import OrderedDict
from typing import Optional, Tuple, Callable, Union
from enum import IntEnum, auto
import struct
import pickle

from uds.common import CompressionMethod, EncryptionMethod, RoutineControlType, DiagnosticSession, UdsTimeoutError, \
    UdsProtocolException, ConditionsNotCorrect

from uds.client import UdsClient

import logging

EXAMPLE_BLOCK_DICT = OrderedDict(
    {"example_block": {"addr": 0x1234,
                       "checksum": bytes(range(15)),
                       "signature": bytes(range(15)),
                       "data": bytes.fromhex("11 22 33 44 55 66 77 88"),
                       "uncompressed_size": 8,
                       "compression_method": CompressionMethod.NO_COMPRESSION,
                       "encryption_method": EncryptionMethod.NO_ENCRYPTION,
                       "transfer_request_parameters": bytes(),
                       "erase_block": False,
                       },
     })

EXAMPLE_PROGRAMMING_FILE_DICT = {"blocks": EXAMPLE_BLOCK_DICT,
                                 "uds_address_and_length_format_identifier": {
                                     # "request_download": (2, 4),
                                     "request_download": "auto",
                                     "routine_control": (2, 4),
                                 },
                                 }


class ProgrammerState(IntEnum):
    """
    The enum for ProgrammerStates
    """
    TestOnly = auto()
    ProgrammingError = auto()
    Init = auto()
    NotConnected = auto()
    PreProgramming = auto()
    SwitchToProgrammingMode = auto()
    UnlockDeviceForProgramming = auto()
    BlockProgramming = auto()
    PostProgramming = auto()
    ProgrammingFinished = auto()


class ProgrammingException(Exception):
    """
    General Programming Error
    """
    pass


class StageException(ProgrammingException):
    """
    The Programming State Job did fail.
    """
    pass


class ProgrammingFileABC(ABC):

    def __init__(self, filepath):
        self._filepath = None
        self._dictionary = None

        self._load_file(filepath=filepath)

    def get_blocks(self):
        return self._dictionary.get("blocks")

    def get_address_and_length_format_identifier(self):
        """
        A method that returns the address and length format identifier defined in the programming file.
        :return: A dictionary with values for various services.
        """
        return self._dictionary.get("uds_address_and_length_format_identifier")

    @abstractmethod
    def _load_file(self, filepath):
        """
        A method to load the ProgrammingFile
        :param filepath: The Filepath
        :return: Nothing
        """


class ExampleProgrammingFile(ProgrammingFileABC):

    def _load_file(self, filepath):
        """
        Load Blocks from pickle file (Testdata)
        :param filepath: The Filepath
        :return: Nothing
        """
        with open(filepath, "rb") as f:
            self._dictionary = pickle.load(f)
        self._filepath = filepath


FILE_EXT_TO_PROGRAMMING_FILE_MAPPING = {".pkl": ExampleProgrammingFile}


class UdsProgrammerABC(ABC):
    """
    Abstract Base Class for an UDS Programmer class
    """

    def __init__(self,
                 client: Optional[UdsClient] = None,
                 programming_filepath: Optional[str] = None,
                 ):
        """
        Constructor

        :param client: A UdsClient for the uds services layer. Optional
                       Theoretically this can be created after reading a programming file.
        :param programming_filepath: The path to a programming file.
                                    It will be loaded automatically.
        """
        self._logger = logging.getLogger(__name__)
        self._client = client
        self._sleep_interval = 1  # 1 second

        self._programming_file = None
        self._expected_identifications = None

        self.state_to_function_dict = {
            ProgrammerState.Init: lambda: ProgrammerState.NotConnected,
            ProgrammerState.NotConnected: self.try_to_connect,
            ProgrammerState.PreProgramming: self.pre_programming,
            ProgrammerState.SwitchToProgrammingMode: self.switch_to_programming_mode,
            ProgrammerState.UnlockDeviceForProgramming: self.unlock_device,
            ProgrammerState.BlockProgramming: self.block_programming,
            ProgrammerState.PostProgramming: self.post_programming,
        }
        self._hooks = []
        self._state = ProgrammerState.Init
        self._current_programming_block = None
        self._current_block_progress = None
        self._worker = None

        if programming_filepath is not None:
            self.load_programming_file(filepath=programming_filepath)

    @property
    def current_programming_block(self) -> Optional[Tuple[str, int, int]]:
        """
        current_programming_block Getter
        :return: A tuple of (block_name, block_number, total_block_number) or None.
        """
        return self._current_programming_block

    @current_programming_block.setter
    def current_programming_block(self, val: Tuple[str, int, int]) -> None:
        """
        current_programming_block Setter
        :param val: A tuple of (block_name, block_number, total_block_number)
        :return: Nothing.
        """
        block_name, block_number, total_block_number = val
        for hook in self._hooks:
            hook({"type": "new_programming_block",
                  "block_name": block_name,
                  "block_number": block_number,
                  "total_block_number": total_block_number
                  })
        self._current_programming_block = val

    @property
    def current_block_progress(self) -> Tuple[int, int]:
        """
        current_block_progress Getter
        :return: A tuple of (current_byte, total_bytes)
        """
        return self._current_block_progress

    @current_block_progress.setter
    def current_block_progress(self, val: Tuple[int, int]) -> None:
        current_byte, total_bytes = val
        for hook in self._hooks:
            hook({"type": "block_progress",
                  "current_byte": current_byte,
                  "total_bytes": total_bytes
                  })
        self._current_block_progress = val

    @property
    def state(self) -> ProgrammerState:
        """
        State Getter
        :return: The Value.
        """
        return self._state

    @state.setter
    def state(self, val: ProgrammerState) -> None:
        """
        State Setter
        :param val: The Value.
        :return: Nothing.
        """
        assert isinstance(val, ProgrammerState)
        if val != self._state:
            for hook in self._hooks:
                hook({"type": "state_transition",
                      "old_state": self._state,
                      "new_state": val,
                      })
            self._logger.debug("Switch State {0} -> {1}".format(self.state.name, val.name))
        self._state = val

    def register_hook(self,
                      hook_function: Callable,
                      ):
        if hook_function not in self._hooks:
            self._hooks.append(hook_function)

    def start_programming(self) -> None:
        """
        This function starts the programming job, e.g. the worker that traverses the state machine.
        :return: Nothing
        """
        assert self._client is not None
        assert self._programming_file is not None
        assert self._worker is None or not self._worker.is_alive()

        self._state = ProgrammerState.Init
        self._worker = threading.Thread(target=self.handle_state_machine)
        self._worker.setDaemon(True)
        self._worker.start()

    def is_finished(self) -> bool:
        """
        Function to check if the programmer has finished the programming job.
        :return: True if finished / False is not.
        """
        return self.state in [ProgrammerState.ProgrammingFinished, ProgrammerState.ProgrammingError, None]

    def handle_state_machine(self):
        """
        The actual worker daemon of this class.
        The state machine uses a Last-In-First-Out-Queue to store the states to be traversed.
        (Note: The names stage, step or state have more or less the same meaning in this context.)
        Using this method, additional / intermediary steps can by dynamically added by the currently handled state, e.g.
        if the UnlockDeviceForProgramming step encounters an error pointing towards a non elapsed barricade timer, it
        can route back to the PreProgramming State by just putting that state and itself back to the queue.
        (Note: This method is Work-in-Progress and has to be perfected while testing.)
        :return: None
        """

        while not self.is_finished():
            job_for_this_state = self.state_to_function_dict.get(self.state)
            if job_for_this_state is not None and callable(job_for_this_state):
                self.state = job_for_this_state()
            else:
                self._logger.error("No job for this state")
                self.state = ProgrammerState.ProgrammingError

    def load_programming_file(self, filepath: str) -> None:
        """
        1st phase of programming. Loading a programming file.
        Although uds has been standardized, the programming sequences have not and basically every EOM has
        their own flavor. Since ODX based formats have emerged, namely PDX, a programming ODX format,
        a programming file provides

        * binary data: the actual binaries to be programmed
        * means of communication with the target device: typically CAN IDs for an ISOTP channel
        * device compatibility checks based on what identification the device provides,
          e.g. a part number is provided by read data by id
        * device unlock and signature methods, e.g. used crypto functions and keys
        * meta data for each binary data:

          * where the binary goes, e.g. address or index of a binary block and
            subsequently if the location has to be erased in case of flash memory
          * precalculated hashes and signatures for binary blocks
          * binary data may be encrypted or compressed and the programming
             application must know this to populate the corresponding uds services

        This abstracted programmer must obtain all necessary information from the programming file.
        A OrderedDict of blocks has to be provided, ordered because because it matters in which sequence
        blocks are programmed. An item must provide meta data on the block, the definition is

        .. code-block:: python

            {
                "blocks":{
                    "example_block": {
                        "addr": 0x1234,
                        "checksum": bytes(range(15)),
                        "signature": bytes(range(15)),
                        "data": bytes.fromhex("11 22 33 44 55 66 77 88"),
                        "uncompressed_size": 8,
                        "compression_method": CompressionMethod.NO_COMPRESSION,
                        "encryption_method": EncryptionMethod.NO_ENCRYPTION,
                        "transfer_request_parameters": bytes(),
                        "erase_block": False,
                    },
                }
                "uds_address_and_length_format_identifier": {"request_download": (2, 4),
                                                             "routine_control": (2, 4),
                                                             },
                }
            }

        There can be general information on communication parameters as well.
        For example, some devices can't handle address items or size items other then 4bytes. In that case the item
        "uds_address_and_length_format_identifier": int, # parameter of request download
        has to be filled. To be continued...
        """
        if os.path.exists(filepath):
            ext = os.path.splitext(filepath)[-1]
            programming_file_class = FILE_EXT_TO_PROGRAMMING_FILE_MAPPING.get(ext)
            if programming_file_class is not None:
                self._programming_file = filepath
                self._programming_file = programming_file_class(filepath=filepath)
            else:
                raise ValueError("No suitable programming file class for extention {0}".format(ext))
        else:
            raise ValueError("Filepath does not exist. {0}".format(filepath))

    ####################################
    # Tasks / Jobs for specific states #
    ####################################

    def try_to_connect(self) -> ProgrammerState:
        """
        A function to check if the programmer which
        by itself is a client, is connected to a server.
        :return: The next state, it can be this state again.
        """
        next_state = self.state
        try:
            self._client.tester_present()
            next_state = ProgrammerState.PreProgramming
        except UdsTimeoutError:
            self._logger.debug("Not Connected - Sleeping {0}".format(self._sleep_interval))
            time.sleep(self._sleep_interval)
        return next_state

    @abstractmethod
    def pre_programming(self) -> ProgrammerState:
        """
        2nd phase of programming
        Pre_programming:
        It consists of a couple of steps that occur linear.

        * Identification Check (Application / Optional)
          In case the programming file provides information or identification patterns on the target device,
          this should be checked against the connected device.
        * Preconditions Check (Application)
          An ECU must perform some task, so it must be asked if it is safe to purge regular operation,
          reboot and stay in bootloader without starting application.
        * Preparations Step (Application)
          Any necessary preparation, e.g. disable the settings of DTCs and stop all unnecessary communication.
          This is not actually plausible because when a programming session is started, the scope of operation
          of the ecu typically is very small, so it would not do anything other than handle diagnostic requests.
          It may even happen that an ECU does tell it's communication partners that it is not available for a limited
          time, i.e. like you tell your neighbors that your on holiday for the weekend, so they don't miss you
          and hopefully water your plants.
        * Transition to Programming Session (Application -> Bootloader)
          The most obvious step last but not least, the start of the programming session, which typically involves
          a reboot to bootloader, and setting some flags before, so bootloader waits for programming instead
          of starting application.
          This phase should also contain a sanity check if the programming session has been reached.

        :return: The next state, typically ProgrammerState.SwitchToProgrammingMode.
        """

    # 3rd phase of programming - the programming in programming session
    # this requires a state machine which is not yet written, however tasks during programming can be
    # abstracted into separate functions.

    def switch_to_programming_mode(self) -> ProgrammerState:
        """
        Switch to Programming Mode
        Typically, a device has a second stage bootloader that has flash programming routines.
        There have been different methods to switch to bootloader operation, the most obvious one is to
        call DiagnosticSessionControl with Value Programming Mode.
        A child class should overwrite this method in case it this step is different.

        :return: The next state, typically ProgrammerState.UnlockDeviceForProgramming.
        """
        next_state = ProgrammerState.ProgrammingError
        try:
            self._client.diagnostic_session_control(session=DiagnosticSession.ProgrammingSession)
            next_state = ProgrammerState.UnlockDeviceForProgramming
        except (UdsTimeoutError, ConditionsNotCorrect) as e:
            self._logger.error("Error {0} occured while switching to programming mode.".format(e))
            pass
        return next_state

    @abstractmethod
    def unlock_device(self) -> ProgrammerState:
        """
        Unlock the device for programming.
        Access to uds services required for programming usually require privileged access that can be gained by
        unlocking the device via security access methods. This procedure should be done in this function.

        :return: The next state, typically ProgrammerState.BlockProgramming.
        """

    def block_programming(self) -> ProgrammerState:
        """
        A universal function for the state block programming.
        :return: The next state, typically ProgrammerState.PostProgramming.
        """
        next_step = ProgrammerState.ProgrammingError
        number_of_programming_blocks = len(self._programming_file.get_blocks())
        addr_size_len = self._programming_file.get_address_and_length_format_identifier().get("request_download")
        try:
            for block_idx, (block_name, block_data) in enumerate(self._programming_file.get_blocks().items()):
                self.current_programming_block = (block_name, block_idx, number_of_programming_blocks)
                self._logger.debug("Programming Block {0}".format(block_name))
                addr = block_data.get("addr")
                data = block_data.get("data")
                erase_block = block_data.get("erase_block")
                compression_method = block_data.get("compression_method")
                encryption_method = block_data.get("encryption_method")
                transfer_request_parameters = block_data.get("transfer_request_parameters")
                size = block_data.get("uncompressed_size")
                checksum = block_data.get("checksum")
                signature = block_data.get("signature")
                self._logger.debug("Pre_block_download Block {0}".format(block_name))
                self.pre_block_download(addr=addr,
                                        erase_block=erase_block)
                self._logger.debug("Download_block {0}".format(block_name))
                self.download_block(addr=addr,
                                    data=data,
                                    size=size,
                                    compression_method=compression_method,
                                    encryption_method=encryption_method,
                                    transfer_request_parameters=transfer_request_parameters,
                                    addr_size_len=addr_size_len)
                self._logger.debug("Post_block_download {0}".format(block_name))
                self.post_block_download(addr=addr,
                                         checksum=checksum,
                                         signature=signature)
                self._logger.debug("Completed Block {0}".format(block_name))
            next_step = ProgrammerState.PostProgramming
        except UdsProtocolException:
            pass

        return next_step

    @abstractmethod
    def pre_block_download(self,
                           addr: int,
                           erase_block: bool,
                           ) -> None:
        """
        Prepare a block download. Subfunction to BlockProgramming State.
        This function intended for block specific tasks before the block is downloaded.
        In general there are multiple things to do when programming a block.
        At first there are hardware constraints. A non-volatile flash memory block needs to be erased
        before it can be programmed again. Therefore the uds client commands the uds server to erase
        that block, typically be routine control uds service.
        Another task may be the use of a journal for a block, e.g. a programming entry, who?, what?, when?,
        how often has the block been programmed, when does it starts to wear out?

        :return: Nothing.
        """

    def download_block(self,
                       addr: int,
                       data: bytes,
                       size: int,
                       addr_size_len: Union[str, Tuple[int, int]] = "auto",
                       compression_method: CompressionMethod = CompressionMethod.NO_COMPRESSION,
                       encryption_method: EncryptionMethod = EncryptionMethod.NO_ENCRYPTION,
                       transfer_request_parameters: bytes = bytes(),
                       ) -> None:
        """
        Download a block, subfunction to Block Programming State.
        This function is universal due to the defined set of uds services for this purpose.
        :param addr: The address of the download.
        :param data: The data to be transferred.
        :param compression_method: The method of compression.
        :param encryption_method: The method of encryption.
        :param transfer_request_parameters: A never used manufacturer specific value.
        :param size: The uncompressed size of the block.
        :param addr_size_len: A tuple of fixed address and size or "auto".
        :return: Nothing.
        """
        self._logger.debug("Download Block - Request Download addr {0} size {1}".format(addr, size))
        resp = self._client.request_download(addr=addr,
                                             size=size,
                                             compression_method=compression_method,
                                             encryption_method=encryption_method,
                                             addr_size_len=addr_size_len)

        block_size = resp.get("max_block_length") - 2
        # The block size apparently is not the binary block but the transmitted block --> -2 bytes protocol overhead

        data_length = len(data)
        current_position = 0
        self.current_block_progress = (current_position, data_length)
        for chunk_idx, chunk_bytes in enumerate(
                [data[idx:idx + block_size] for idx in range(0, len(data), block_size)]):
            self._logger.debug(
                "Download Block - Transfer Data Block {0} Size {1}".format(chunk_idx + 1, len(chunk_bytes)))
            self._client.transfer_data(block_sequence_counter=chunk_idx + 1,
                                       data=chunk_bytes)
            current_position += len(chunk_bytes)
            self.current_block_progress = (current_position, data_length)
        self._logger.debug("Download Block - Request Transfer Exit")
        self._client.request_transfer_exit(transfer_request_parameters=transfer_request_parameters)
        self._logger.debug("Download Block - Complete")

    @abstractmethod
    def post_block_download(self,
                            addr: int,
                            checksum: bytes,
                            signature: bytes,
                            ) -> None:
        """
        Check a block after download. Subfunction to Block Programming State
        This function is intended for block specific tasks after a block was downloaded.
        Typical task is a check for data integrity, e.g. the uds client starts a checksum routine
        on the uds server and either provides the expected checksum for check or the uds server sends
        the checksum back, so the client can compare and decide what to do.
        There may also be crypto involved, e.g. a signature check.

        :return: Nothing.
        """

    @abstractmethod
    def post_programming(self) -> ProgrammerState:
        """
        Post programming.
        This function is intended for the big cleanup after the block programming has happened.
        The goal is to have the freshly programmed device resume it's tasks by starting application again.
        This is usually done by switching back to default session or calling ecu reset.
        After the device is running application again, it may also be needed to re-enable services that have
        been disabled in pre programming step.
        :return: The next state, typically ProgrammerState.ProgrammingFinished.
        """


class ExampleUdsProgrammer(UdsProgrammerABC):

    def pre_programming(self) -> ProgrammerState:
        """
        Check if the logical preconditions for programming are fulfilled.
        You won't flash an engine ecu while the engine is running, would you?
        Well it can be done in some rare cases.
        :return: The next state.
        """
        next_state = ProgrammerState.ProgrammingError
        try:
            check_programming_did = 0xBEEF
            data = self._client.read_data_by_id(did=check_programming_did).get("data")
            status = bool.from_bytes(data, "big")
            if status:
                next_state = ProgrammerState.SwitchToProgrammingMode
        except UdsProtocolException:
            pass
        return next_state

    def unlock_device(self) -> ProgrammerState:
        """
        Execute seed and key routine to unlock the device.
        :return: The next state.
        """
        next_state = ProgrammerState.ProgrammingError
        try:
            security_level = 1
            seed = self._client.security_access(security_level=security_level).get("seed")
            key = struct.pack(">I", struct.unpack(">I", seed)[0] + 1)
            self._client.security_access(security_level=security_level + 1, key=key)
            next_state = ProgrammerState.BlockProgramming
        except UdsProtocolException:
            pass
        return next_state

    def pre_block_download(self,
                           addr: int,
                           erase_block: bool,
                           ) -> None:
        """
        Write the workshop name into the device for
        an easy example.
        :param addr: The address of the block.
        :param erase_block: The erase flag.
        :return: Nothing
        """
        workshop_did = 0xCAFE
        self._client.write_data_by_id(did=workshop_did, data="1234".encode())

    def post_block_download(self,
                            addr: int,
                            checksum: bytes,
                            signature: bytes,
                            ) -> None:
        """
        Execute a check routine in device.
        :param addr: The address of the block.
        :param checksum: The block checksum.
        :param signature: The block signature.
        :return: Nothing.
        """
        self._client.routine_control(routine_control_type=RoutineControlType.StartRoutine,
                                     routine_id=0x1234,
                                     data=bytes.fromhex("11 22 33 44 55 66 77 88"))

    def post_programming(self) -> ProgrammerState:
        """
        Write the programming date for an easy example.
        :return: Nothing.
        """
        programming_date_did = 0x4242
        self._client.write_data_by_id(did=programming_date_did, data=bytes.fromhex("11 22 33 44"))
        return ProgrammerState.ProgrammingFinished
