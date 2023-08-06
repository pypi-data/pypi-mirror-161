
'Generated protocol buffer code.'
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1ctendermint/store/types.proto\x12\x10tendermint.store"/\n\x0fBlockStoreState\x12\x0c\n\x04base\x18\x01 \x01(\x03\x12\x0e\n\x06height\x18\x02 \x01(\x03B9Z7github.com/tendermint/tendermint/proto/tendermint/storeb\x06proto3')
_BLOCKSTORESTATE = DESCRIPTOR.message_types_by_name['BlockStoreState']
BlockStoreState = _reflection.GeneratedProtocolMessageType('BlockStoreState', (_message.Message,), {'DESCRIPTOR': _BLOCKSTORESTATE, '__module__': 'tendermint.store.types_pb2'})
_sym_db.RegisterMessage(BlockStoreState)
if (_descriptor._USE_C_DESCRIPTORS == False):
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b'Z7github.com/tendermint/tendermint/proto/tendermint/store'
    _BLOCKSTORESTATE._serialized_start = 50
    _BLOCKSTORESTATE._serialized_end = 97
