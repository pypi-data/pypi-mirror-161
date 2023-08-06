from typing import overload
import typing

import System
import System.Runtime.InteropServices.Marshalling

System_Runtime_InteropServices_Marshalling_SpanMarshaller_T = typing.TypeVar("System_Runtime_InteropServices_Marshalling_SpanMarshaller_T")
System_Runtime_InteropServices_Marshalling_SpanMarshaller_TUnmanagedElement = typing.TypeVar("System_Runtime_InteropServices_Marshalling_SpanMarshaller_TUnmanagedElement")
System_Runtime_InteropServices_Marshalling_ArrayMarshaller_T = typing.TypeVar("System_Runtime_InteropServices_Marshalling_ArrayMarshaller_T")
System_Runtime_InteropServices_Marshalling_ArrayMarshaller_TUnmanagedElement = typing.TypeVar("System_Runtime_InteropServices_Marshalling_ArrayMarshaller_TUnmanagedElement")
System_Runtime_InteropServices_Marshalling_PointerArrayMarshaller_T = typing.TypeVar("System_Runtime_InteropServices_Marshalling_PointerArrayMarshaller_T")
System_Runtime_InteropServices_Marshalling_PointerArrayMarshaller_TUnmanagedElement = typing.TypeVar("System_Runtime_InteropServices_Marshalling_PointerArrayMarshaller_TUnmanagedElement")
System_Runtime_InteropServices_Marshalling_ReadOnlySpanMarshaller_T = typing.TypeVar("System_Runtime_InteropServices_Marshalling_ReadOnlySpanMarshaller_T")
System_Runtime_InteropServices_Marshalling_ReadOnlySpanMarshaller_TUnmanagedElement = typing.TypeVar("System_Runtime_InteropServices_Marshalling_ReadOnlySpanMarshaller_TUnmanagedElement")


class MarshalUsingAttribute(System.Attribute):
    """Attribute used to provide a custom marshaller type or size information for marshalling."""

    @property
    def NativeType(self) -> typing.Type:
        """The marshaller type used to convert the attributed type from managed to native code. This type must be attributed with CustomMarshallerAttribute"""
        ...

    @property
    def CountElementName(self) -> str:
        """The name of the parameter that will provide the size of the collection when marshalling from unmanaged to managed, or ReturnsCountValue if the return value provides the size."""
        ...

    @CountElementName.setter
    def CountElementName(self, value: str):
        """The name of the parameter that will provide the size of the collection when marshalling from unmanaged to managed, or ReturnsCountValue if the return value provides the size."""
        ...

    @property
    def ConstantElementCount(self) -> int:
        """If a collection is constant size, the size of the collection when marshalling from unmanaged to managed."""
        ...

    @ConstantElementCount.setter
    def ConstantElementCount(self, value: int):
        """If a collection is constant size, the size of the collection when marshalling from unmanaged to managed."""
        ...

    @property
    def ElementIndirectionDepth(self) -> int:
        """What indirection depth this marshalling info is provided for."""
        ...

    @ElementIndirectionDepth.setter
    def ElementIndirectionDepth(self, value: int):
        """What indirection depth this marshalling info is provided for."""
        ...

    ReturnsCountValue: str = "return-value"
    """A constant string that represents the name of the return value for CountElementName."""

    @overload
    def __init__(self) -> None:
        """Create a MarshalUsingAttribute that provides only size information."""
        ...

    @overload
    def __init__(self, nativeType: typing.Type) -> None:
        """
        Create a MarshalUsingAttribute that provides a native marshalling type and optionally size information.
        
        :param nativeType: The marshaller type used to convert the attributed type from managed to native code. This type must be attributed with CustomMarshallerAttribute
        """
        ...


class NativeMarshallingAttribute(System.Attribute):
    """Attribute used to provide a default custom marshaller type for a given managed type."""

    @property
    def NativeType(self) -> typing.Type:
        """The marshaller type used to convert the attributed type from managed to native code. This type must be attributed with CustomMarshallerAttribute"""
        ...

    def __init__(self, nativeType: typing.Type) -> None:
        """
        Create a NativeMarshallingAttribute that provides a native marshalling type.
        
        :param nativeType: The marshaller type used to convert the attributed type from managed to native code. This type must be attributed with CustomMarshallerAttribute
        """
        ...


class SpanMarshaller(typing.Generic[System_Runtime_InteropServices_Marshalling_SpanMarshaller_T, System_Runtime_InteropServices_Marshalling_SpanMarshaller_TUnmanagedElement], System.Object):
    """
    The SpanMarshaller{T, TUnmanagedElement} type supports marshalling a Span{T} from managed value
    to a contiguous native array of the unmanaged values of the elements.
    """

    class ManagedToUnmanagedIn:
        """The marshaller type that supports marshalling from managed into unmanaged in a call from managed code to unmanaged code."""

        BufferSize: int

        def Free(self) -> None:
            """Frees resources."""
            ...

        def FromManaged(self, managed: System.Span[System_Runtime_InteropServices_Marshalling_SpanMarshaller_T], buffer: System.Span[System_Runtime_InteropServices_Marshalling_SpanMarshaller_TUnmanagedElement]) -> None:
            """
            Initializes the SpanMarshaller{T, TUnmanagedElement}.ManagedToUnmanagedIn marshaller.
            
            :param managed: Span to be marshalled.
            :param buffer: Buffer that may be used for marshalling.
            """
            ...

        def GetManagedValuesSource(self) -> System.ReadOnlySpan[System_Runtime_InteropServices_Marshalling_SpanMarshaller_T]:
            """
            Gets a span that points to the memory where the managed values of the array are stored.
            
            :returns: Span over managed values of the array.
            """
            ...

        @overload
        def GetPinnableReference(self) -> typing.Any:
            """Returns a reference to the marshalled array."""
            ...

        @staticmethod
        @overload
        def GetPinnableReference(managed: System.Span[System_Runtime_InteropServices_Marshalling_SpanMarshaller_T]) -> typing.Any:
            """
            Gets a pinnable reference to the managed span.
            
            :param managed: The managed span.
            :returns: A reference that can be pinned and directly passed to unmanaged code.
            """
            ...

        def GetUnmanagedValuesDestination(self) -> System.Span[System_Runtime_InteropServices_Marshalling_SpanMarshaller_TUnmanagedElement]:
            """
            Returns a span that points to the memory where the unmanaged values of the array should be stored.
            
            :returns: Span where unmanaged values of the array should be stored.
            """
            ...

        def ToUnmanaged(self) -> typing.Any:
            """Returns the unmanaged value representing the array."""
            ...

    @staticmethod
    def AllocateContainerForManagedElements(unmanaged: typing.Any, numElements: int) -> System.Span[System_Runtime_InteropServices_Marshalling_SpanMarshaller_T]:
        """
        Allocate the space to store the managed elements.
        
        :param unmanaged: The unmanaged value.
        :param numElements: The number of elements in the unmanaged collection.
        :returns: A span over enough memory to contain  elements.
        """
        ...

    @staticmethod
    def AllocateContainerForUnmanagedElements(managed: System.Span[System_Runtime_InteropServices_Marshalling_SpanMarshaller_T], numElements: typing.Optional[int]) -> typing.Union[typing.Any, int]:
        """
        Allocate the space to store the unmanaged elements.
        
        :param managed: The managed span.
        :param numElements: The number of elements in the span.
        :returns: A pointer to the block of memory for the unmanaged elements.
        """
        ...

    @staticmethod
    def Free(unmanaged: typing.Any) -> None:
        """
        Free the allocated unmanaged memory.
        
        :param unmanaged: Allocated unmanaged memory
        """
        ...

    @staticmethod
    def GetManagedValuesDestination(managed: System.Span[System_Runtime_InteropServices_Marshalling_SpanMarshaller_T]) -> System.Span[System_Runtime_InteropServices_Marshalling_SpanMarshaller_T]:
        """
        Get a span of the space where the managed collection elements should be stored.
        
        :param managed: A span over the space to store the managed elements
        :returns: A span over the managed memory that can contain the specified number of elements.
        """
        ...

    @staticmethod
    def GetManagedValuesSource(managed: System.Span[System_Runtime_InteropServices_Marshalling_SpanMarshaller_T]) -> System.ReadOnlySpan[System_Runtime_InteropServices_Marshalling_SpanMarshaller_T]:
        """
        Get a span of the managed collection elements.
        
        :param managed: The managed collection.
        :returns: A span of the managed collection elements.
        """
        ...

    @staticmethod
    def GetUnmanagedValuesDestination(unmanaged: typing.Any, numElements: int) -> System.Span[System_Runtime_InteropServices_Marshalling_SpanMarshaller_TUnmanagedElement]:
        """
        Get a span of the space where the unmanaged collection elements should be stored.
        
        :param unmanaged: The pointer to the block of memory for the unmanaged elements.
        :param numElements: The number of elements that will be copied into the memory block.
        :returns: A span over the unmanaged memory that can contain the specified number of elements.
        """
        ...

    @staticmethod
    def GetUnmanagedValuesSource(unmanaged: typing.Any, numElements: int) -> System.ReadOnlySpan[System_Runtime_InteropServices_Marshalling_SpanMarshaller_TUnmanagedElement]:
        """
        Get a span of the native collection elements.
        
        :param unmanaged: The unmanaged value.
        :param numElements: The number of elements in the unmanaged collection.
        :returns: A span over the native collection elements.
        """
        ...


class MarshalMode(System.Enum):
    """An enumeration representing the different marshalling modes in our marshalling model."""

    Default = 0
    """
    All modes. A marshaller specified with this mode will be used if there is not a specific
    marshaller specified for a given usage mode.
    """

    ManagedToUnmanagedIn = 1
    """By-value and in parameters in managed-to-unmanaged scenarios, like P/Invoke."""

    ManagedToUnmanagedRef = 2
    """ref parameters in managed-to-unmanaged scenarios, like P/Invoke."""

    ManagedToUnmanagedOut = 3
    """out parameters in managed-to-unmanaged scenarios, like P/Invoke."""

    UnmanagedToManagedIn = 4
    """By-value and in parameters in unmanaged-to-managed scenarios, like Reverse P/Invoke."""

    UnmanagedToManagedRef = 5
    """ref parameters in unmanaged-to-managed scenarios, like Reverse P/Invoke."""

    UnmanagedToManagedOut = 6
    """out parameters in unmanaged-to-managed scenarios, like Reverse P/Invoke."""

    ElementIn = 7
    """Elements of arrays passed with in or by-value in interop scenarios."""

    ElementRef = 8
    """Elements of arrays passed with ref or passed by-value with both InAttribute and OutAttribute in interop scenarios."""

    ElementOut = 9
    """Elements of arrays passed with out or passed by-value with only OutAttribute in interop scenarios."""


class AnsiStringMarshaller(System.Object):
    """Marshaller for ANSI strings"""

    class ManagedToUnmanagedIn:
        """Custom marshaller to marshal a managed string as a ANSI unmanaged string."""

        BufferSize: int
        """Requested buffer size for optimized marshalling."""

        def Free(self) -> None:
            """Free any allocated unmanaged string."""
            ...

        def FromManaged(self, managed: str, buffer: System.Span[int]) -> None:
            """
            Initialize the marshaller with a managed string and requested buffer.
            
            :param managed: The managed string
            :param buffer: A request buffer of at least size, BufferSize.
            """
            ...

        def ToUnmanaged(self) -> typing.Any:
            """
            Convert the current manage string to an unmanaged string.
            
            :returns: The unmanaged string.
            """
            ...

    @staticmethod
    def ConvertToManaged(unmanaged: typing.Any) -> str:
        """
        Convert an unmanaged string to a managed version.
        
        :param unmanaged: An unmanaged string
        :returns: A managed string.
        """
        ...

    @staticmethod
    def ConvertToUnmanaged(managed: str) -> typing.Any:
        """
        Convert a string to an unmanaged version.
        
        :param managed: A managed string
        :returns: An unmanaged string.
        """
        ...

    @staticmethod
    def Free(unmanaged: typing.Any) -> None:
        """
        Free the memory for the unmanaged string.
        
        :param unmanaged: Memory allocated for the unmanaged string.
        """
        ...


class Utf8StringMarshaller(System.Object):
    """Marshaller for UTF-8 strings"""

    class ManagedToUnmanagedIn:
        """Custom marshaller to marshal a managed string as a UTF-8 unmanaged string."""

        BufferSize: int
        """Requested buffer size for optimized marshalling."""

        def Free(self) -> None:
            """Free any allocated unmanaged string."""
            ...

        def FromManaged(self, managed: str, buffer: System.Span[int]) -> None:
            """
            Initialize the marshaller with a managed string and requested buffer.
            
            :param managed: The managed string
            :param buffer: A request buffer of at least size, BufferSize.
            """
            ...

        def ToUnmanaged(self) -> typing.Any:
            """
            Convert the current manage string to an unmanaged string.
            
            :returns: The unmanaged string.
            """
            ...

    @staticmethod
    def ConvertToManaged(unmanaged: typing.Any) -> str:
        """
        Convert an unmanaged string to a managed version.
        
        :param unmanaged: An unmanaged string
        :returns: A managed string.
        """
        ...

    @staticmethod
    def ConvertToUnmanaged(managed: str) -> typing.Any:
        """
        Convert a string to an unmanaged version.
        
        :param managed: A managed string
        :returns: An unmanaged string.
        """
        ...

    @staticmethod
    def Free(unmanaged: typing.Any) -> None:
        """
        Free the memory for the unmanaged string.
        
        :param unmanaged: Memory allocated for the unmanaged string.
        """
        ...


class ArrayMarshaller(typing.Generic[System_Runtime_InteropServices_Marshalling_ArrayMarshaller_T, System_Runtime_InteropServices_Marshalling_ArrayMarshaller_TUnmanagedElement], System.Object):
    """Marshaller for arrays"""

    class ManagedToUnmanagedIn:
        """Marshaller for marshalling a array from managed to unmanaged."""

        BufferSize: int
        """Requested caller-allocated buffer size."""

        def Free(self) -> None:
            """Frees resources."""
            ...

        def FromManaged(self, array: typing.List[System_Runtime_InteropServices_Marshalling_ArrayMarshaller_T], buffer: System.Span[System_Runtime_InteropServices_Marshalling_ArrayMarshaller_TUnmanagedElement]) -> None:
            """
            Initializes the ArrayMarshaller{T, TUnmanagedElement}.ManagedToUnmanagedIn marshaller.
            
            :param array: Array to be marshalled.
            :param buffer: Buffer that may be used for marshalling.
            """
            ...

        def GetManagedValuesSource(self) -> System.ReadOnlySpan[System_Runtime_InteropServices_Marshalling_ArrayMarshaller_T]:
            """
            Gets a span that points to the memory where the managed values of the array are stored.
            
            :returns: Span over managed values of the array.
            """
            ...

        @overload
        def GetPinnableReference(self) -> typing.Any:
            """Returns a reference to the marshalled array."""
            ...

        @staticmethod
        @overload
        def GetPinnableReference(array: typing.List[System_Runtime_InteropServices_Marshalling_ArrayMarshaller_T]) -> typing.Any:
            """
            Gets a pinnable reference to the managed array.
            
            :param array: The managed array.
            :returns: The reference that can be pinned and directly passed to unmanaged code.
            """
            ...

        def GetUnmanagedValuesDestination(self) -> System.Span[System_Runtime_InteropServices_Marshalling_ArrayMarshaller_TUnmanagedElement]:
            """
            Returns a span that points to the memory where the unmanaged values of the array should be stored.
            
            :returns: Span where unmanaged values of the array should be stored.
            """
            ...

        def ToUnmanaged(self) -> typing.Any:
            """Returns the unmanaged value representing the array."""
            ...

    @staticmethod
    def AllocateContainerForManagedElements(unmanaged: typing.Any, numElements: int) -> typing.List[System_Runtime_InteropServices_Marshalling_ArrayMarshaller_T]:
        """
        Allocates memory for the managed representation of the array.
        
        :param unmanaged: The unmanaged array
        :param numElements: The unmanaged element count
        :returns: The managed array.
        """
        ...

    @staticmethod
    def AllocateContainerForUnmanagedElements(managed: typing.List[System_Runtime_InteropServices_Marshalling_ArrayMarshaller_T], numElements: typing.Optional[int]) -> typing.Union[typing.Any, int]:
        """
        Allocates memory for the unmanaged representation of the array.
        
        :param managed: The managed array
        :param numElements: The unmanaged element count
        :returns: The unmanaged pointer to the allocated memory.
        """
        ...

    @staticmethod
    def Free(unmanaged: typing.Any) -> None:
        """
        Frees memory for the unmanaged array.
        
        :param unmanaged: Unmanaged array
        """
        ...

    @staticmethod
    def GetManagedValuesDestination(managed: typing.List[System_Runtime_InteropServices_Marshalling_ArrayMarshaller_T]) -> System.Span[System_Runtime_InteropServices_Marshalling_ArrayMarshaller_T]:
        """
        Gets a destination for the managed elements in the array.
        
        :param managed: The managed array
        :returns: The Span{T} of managed elements.
        """
        ...

    @staticmethod
    def GetManagedValuesSource(managed: typing.List[System_Runtime_InteropServices_Marshalling_ArrayMarshaller_T]) -> System.ReadOnlySpan[System_Runtime_InteropServices_Marshalling_ArrayMarshaller_T]:
        """
        Gets a source for the managed elements in the array.
        
        :param managed: The managed array
        :returns: The ReadOnlySpan{T} containing the managed elements to marshal.
        """
        ...

    @staticmethod
    def GetUnmanagedValuesDestination(unmanaged: typing.Any, numElements: int) -> System.Span[System_Runtime_InteropServices_Marshalling_ArrayMarshaller_TUnmanagedElement]:
        """
        Gets a destination for the unmanaged elements in the array.
        
        :param unmanaged: The unmanaged allocation
        :param numElements: The unmanaged element count
        :returns: The Span{TUnmanagedElement} of unmanaged elements.
        """
        ...

    @staticmethod
    def GetUnmanagedValuesSource(unmanagedValue: typing.Any, numElements: int) -> System.ReadOnlySpan[System_Runtime_InteropServices_Marshalling_ArrayMarshaller_TUnmanagedElement]:
        """
        Gets a source for the unmanaged elements in the array.
        
        :param unmanagedValue: The unmanaged array
        :param numElements: The unmanaged element count
        :returns: The ReadOnlySpan{TUnmanagedElement} containing the unmanaged elements to marshal.
        """
        ...


class ContiguousCollectionMarshallerAttribute(System.Attribute):
    """Specifies that this marshaller entry-point type is a contiguous collection marshaller."""


class PointerArrayMarshaller(typing.Generic[System_Runtime_InteropServices_Marshalling_PointerArrayMarshaller_T, System_Runtime_InteropServices_Marshalling_PointerArrayMarshaller_TUnmanagedElement], System.Object):
    """Marshaller for arrays of pointers"""

    class ManagedToUnmanagedIn:
        """Marshaller for marshalling a array from managed to unmanaged."""

        BufferSize: int
        """Requested caller-allocated buffer size."""

        def Free(self) -> None:
            """Frees resources."""
            ...

        def FromManaged(self, array: typing.List[typing.Any], buffer: System.Span[System_Runtime_InteropServices_Marshalling_PointerArrayMarshaller_TUnmanagedElement]) -> None:
            """
            Initializes the PointerArrayMarshaller{T, TUnmanagedElement}.ManagedToUnmanagedIn marshaller.
            
            :param array: Array to be marshalled.
            :param buffer: Buffer that may be used for marshalling.
            """
            ...

        def GetManagedValuesSource(self) -> System.ReadOnlySpan[System.IntPtr]:
            """
            Gets a span that points to the memory where the managed values of the array are stored.
            
            :returns: Span over managed values of the array.
            """
            ...

        @overload
        def GetPinnableReference(self) -> typing.Any:
            """Returns a reference to the marshalled array."""
            ...

        @staticmethod
        @overload
        def GetPinnableReference(array: typing.List[typing.Any]) -> typing.Any:
            """
            Gets a pinnable reference to the managed array.
            
            :param array: The managed array.
            :returns: The reference that can be pinned and directly passed to unmanaged code.
            """
            ...

        def GetUnmanagedValuesDestination(self) -> System.Span[System_Runtime_InteropServices_Marshalling_PointerArrayMarshaller_TUnmanagedElement]:
            """
            Returns a span that points to the memory where the unmanaged values of the array should be stored.
            
            :returns: Span where unmanaged values of the array should be stored.
            """
            ...

        def ToUnmanaged(self) -> typing.Any:
            """Returns the unmanaged value representing the array."""
            ...

    @staticmethod
    def AllocateContainerForManagedElements(unmanaged: typing.Any, numElements: int) -> typing.List[typing.Any]:
        """
        Allocates memory for the managed representation of the array.
        
        :param unmanaged: The unmanaged array
        :param numElements: The unmanaged element count
        :returns: The managed array.
        """
        ...

    @staticmethod
    def AllocateContainerForUnmanagedElements(managed: typing.List[typing.Any], numElements: typing.Optional[int]) -> typing.Union[typing.Any, int]:
        """
        Allocates memory for the unmanaged representation of the array.
        
        :param managed: The managed array to marshal
        :param numElements: The unmanaged element count
        :returns: The unmanaged pointer to the allocated memory.
        """
        ...

    @staticmethod
    def Free(unmanaged: typing.Any) -> None:
        """
        Frees memory for the unmanaged array.
        
        :param unmanaged: Unmanaged array
        """
        ...

    @staticmethod
    def GetManagedValuesDestination(managed: typing.List[typing.Any]) -> System.Span[System.IntPtr]:
        """
        Gets a destination for the managed elements in the array.
        
        :param managed: The managed array
        :returns: The Span{T} of managed elements.
        """
        ...

    @staticmethod
    def GetManagedValuesSource(managed: typing.List[typing.Any]) -> System.ReadOnlySpan[System.IntPtr]:
        """
        Gets a source for the managed elements in the array.
        
        :param managed: The managed array
        :returns: The ReadOnlySpan{IntPtr} containing the managed elements to marshal.
        """
        ...

    @staticmethod
    def GetUnmanagedValuesDestination(unmanaged: typing.Any, numElements: int) -> System.Span[System_Runtime_InteropServices_Marshalling_PointerArrayMarshaller_TUnmanagedElement]:
        """
        Gets a destination for the unmanaged elements in the array.
        
        :param unmanaged: The unmanaged allocation
        :param numElements: The unmanaged element count
        :returns: The Span{TUnmanagedElement} of unmanaged elements.
        """
        ...

    @staticmethod
    def GetUnmanagedValuesSource(unmanagedValue: typing.Any, numElements: int) -> System.ReadOnlySpan[System_Runtime_InteropServices_Marshalling_PointerArrayMarshaller_TUnmanagedElement]:
        """
        Gets a source for the unmanaged elements in the array.
        
        :param unmanagedValue: The unmanaged array
        :param numElements: The unmanaged element count
        :returns: The ReadOnlySpan{TUnmanagedElement} containing the unmanaged elements to marshal.
        """
        ...


class ReadOnlySpanMarshaller(typing.Generic[System_Runtime_InteropServices_Marshalling_ReadOnlySpanMarshaller_T, System_Runtime_InteropServices_Marshalling_ReadOnlySpanMarshaller_TUnmanagedElement], System.Object):
    """
    The ReadOnlySpanMarshaller{T, TUnmanagedElement} type supports marshalling a ReadOnlySpan{T} from managed value
    to a contiguous native array of the unmanaged values of the elements.
    """

    class UnmanagedToManagedOut(System.Object):
        """The marshaller type that supports marshalling from managed into unmanaged in a call from unmanaged code to managed code."""

        @staticmethod
        def AllocateContainerForUnmanagedElements(managed: System.ReadOnlySpan[System_Runtime_InteropServices_Marshalling_ReadOnlySpanMarshaller_T], numElements: typing.Optional[int]) -> typing.Union[typing.Any, int]:
            """
            Allocate the space to store the unmanaged elements.
            
            :param managed: The managed span.
            :param numElements: The number of elements in the span.
            :returns: A pointer to the block of memory for the unmanaged elements.
            """
            ...

        @staticmethod
        def GetManagedValuesSource(managed: System.ReadOnlySpan[System_Runtime_InteropServices_Marshalling_ReadOnlySpanMarshaller_T]) -> System.ReadOnlySpan[System_Runtime_InteropServices_Marshalling_ReadOnlySpanMarshaller_T]:
            """
            Get a span of the managed collection elements.
            
            :param managed: The managed collection.
            :returns: A span of the managed collection elements.
            """
            ...

        @staticmethod
        def GetUnmanagedValuesDestination(unmanaged: typing.Any, numElements: int) -> System.Span[System_Runtime_InteropServices_Marshalling_ReadOnlySpanMarshaller_TUnmanagedElement]:
            """
            Get a span of the space where the unmanaged collection elements should be stored.
            
            :param unmanaged: The pointer to the block of memory for the unmanaged elements.
            :param numElements: The number of elements that will be copied into the memory block.
            :returns: A span over the unmanaged memory that can contain the specified number of elements.
            """
            ...

    class ManagedToUnmanagedIn:
        """The marshaller type that supports marshalling from managed into unmanaged in a call from managed code to unmanaged code."""

        BufferSize: int
        """The size of the caller-allocated buffer to allocate."""

        def Free(self) -> None:
            """Frees resources."""
            ...

        def FromManaged(self, managed: System.ReadOnlySpan[System_Runtime_InteropServices_Marshalling_ReadOnlySpanMarshaller_T], buffer: System.Span[System_Runtime_InteropServices_Marshalling_ReadOnlySpanMarshaller_TUnmanagedElement]) -> None:
            """
            Initializes the SpanMarshaller{T, TUnmanagedElement}.ManagedToUnmanagedIn marshaller.
            
            :param managed: Span to be marshalled.
            :param buffer: Buffer that may be used for marshalling.
            """
            ...

        def GetManagedValuesSource(self) -> System.ReadOnlySpan[System_Runtime_InteropServices_Marshalling_ReadOnlySpanMarshaller_T]:
            """
            Gets a span that points to the memory where the managed values of the array are stored.
            
            :returns: Span over managed values of the array.
            """
            ...

        @overload
        def GetPinnableReference(self) -> typing.Any:
            """Returns a reference to the marshalled array."""
            ...

        @staticmethod
        @overload
        def GetPinnableReference(managed: System.ReadOnlySpan[System_Runtime_InteropServices_Marshalling_ReadOnlySpanMarshaller_T]) -> typing.Any:
            """
            Pin the managed span to a pointer to pass directly to unmanaged code.
            
            :param managed: The managed span.
            :returns: A reference that can be pinned and directly passed to unmanaged code.
            """
            ...

        def GetUnmanagedValuesDestination(self) -> System.Span[System_Runtime_InteropServices_Marshalling_ReadOnlySpanMarshaller_TUnmanagedElement]:
            """
            Returns a span that points to the memory where the unmanaged values of the array should be stored.
            
            :returns: Span where unmanaged values of the array should be stored.
            """
            ...

        def ToUnmanaged(self) -> typing.Any:
            """Returns the unmanaged value representing the array."""
            ...


class CustomMarshallerAttribute(System.Attribute):
    """Attribute to indicate an entry point type for defining a marshaller."""

    class GenericPlaceholder:
        """Placeholder type for generic parameter"""

    @property
    def ManagedType(self) -> typing.Type:
        """The managed type to marshal."""
        ...

    @property
    def MarshalMode(self) -> int:
        """
        The marshalling mode this attribute applies to.
        
        This property contains the int value of a member of the System.Runtime.InteropServices.Marshalling.MarshalMode enum.
        """
        ...

    @property
    def MarshallerType(self) -> typing.Type:
        """Type used for marshalling."""
        ...

    def __init__(self, managedType: typing.Type, marshalMode: System.Runtime.InteropServices.Marshalling.MarshalMode, marshallerType: typing.Type) -> None:
        """
        Create a CustomMarshallerAttribute instance.
        
        :param managedType: Managed type to marshal.
        :param marshalMode: The marshalling mode this attribute applies to.
        :param marshallerType: Type used for marshalling.
        """
        ...


class BStrStringMarshaller(System.Object):
    """Marshaller for BSTR strings"""

    class ManagedToUnmanagedIn:
        """Custom marshaller to marshal a managed string as a ANSI unmanaged string."""

        BufferSize: int
        """Requested buffer size for optimized marshalling."""

        def Free(self) -> None:
            """Free any allocated unmanaged string."""
            ...

        def FromManaged(self, managed: str, buffer: System.Span[int]) -> None:
            """
            Initialize the marshaller with a managed string and requested buffer.
            
            :param managed: The managed string
            :param buffer: A request buffer of at least size, BufferSize.
            """
            ...

        def ToUnmanaged(self) -> typing.Any:
            """
            Convert the current manage string to an unmanaged string.
            
            :returns: The unmanaged string.
            """
            ...

    @staticmethod
    def ConvertToManaged(unmanaged: typing.Any) -> str:
        """
        Convert an unmanaged string to a managed version.
        
        :param unmanaged: An unmanaged string
        :returns: A managed string.
        """
        ...

    @staticmethod
    def ConvertToUnmanaged(managed: str) -> typing.Any:
        """
        Convert a string to an unmanaged version.
        
        :param managed: A managed string
        :returns: An unmanaged string.
        """
        ...

    @staticmethod
    def Free(unmanaged: typing.Any) -> None:
        """
        Free the memory for the unmanaged string.
        
        :param unmanaged: Memory allocated for the unmanaged string.
        """
        ...


class Utf16StringMarshaller(System.Object):
    """Marshaller for UTF-16 strings"""

    @staticmethod
    def ConvertToManaged(unmanaged: typing.Any) -> str:
        """
        Convert an unmanaged string to a managed version.
        
        :param unmanaged: An unmanaged string
        :returns: A managed string.
        """
        ...

    @staticmethod
    def ConvertToUnmanaged(managed: str) -> typing.Any:
        """
        Convert a string to an unmanaged version.
        
        :param managed: A managed string
        :returns: An unmanaged string.
        """
        ...

    @staticmethod
    def Free(unmanaged: typing.Any) -> None:
        """
        Free the memory for the unmanaged string.
        
        :param unmanaged: Memory allocated for the unmanaged string.
        """
        ...

    @staticmethod
    def GetPinnableReference(str: str) -> typing.Any:
        """
        Get a pinnable reference for the string.
        
        :param str: The string.
        :returns: A pinnable reference.
        """
        ...


