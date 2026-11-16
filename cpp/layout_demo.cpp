#include "packed_record.hpp"
#include <cstddef>
#include <iostream>

std::size_t peer_host_size();
std::size_t peer_host_offset();
std::size_t peer_wire_size();

static_assert(sizeof(PackedRecord) == 5, "synthetic packed record must occupy 5 bytes");
static_assert(offsetof(PackedRecord, sequence) == 1, "packed field offset mismatch");
static_assert(alignof(HostRecord) >= alignof(double), "packing leaked into ordinary record");
static_assert(offsetof(HostRecord, value) % alignof(double) == 0, "natural alignment lost");

int main() {
    if (peer_host_size() != sizeof(HostRecord) ||
        peer_host_offset() != offsetof(HostRecord, value) ||
        peer_wire_size() != sizeof(PackedRecord)) return 1;
    std::cout << "packed bytes=" << sizeof(PackedRecord)
              << "; host bytes=" << sizeof(HostRecord)
              << "; natural double offset=" << offsetof(HostRecord, value) << '\n';
}
