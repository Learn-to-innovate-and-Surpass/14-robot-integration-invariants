#include "packed_record.hpp"
#include <cstddef>

std::size_t peer_host_size() { return sizeof(HostRecord); }
std::size_t peer_host_offset() { return offsetof(HostRecord, value); }
std::size_t peer_wire_size() { return sizeof(PackedRecord); }
