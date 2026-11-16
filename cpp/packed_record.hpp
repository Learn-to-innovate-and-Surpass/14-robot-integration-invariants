#ifndef SYNTHETIC_PACKED_RECORD_HPP
#define SYNTHETIC_PACKED_RECORD_HPP
#include <cstdint>

// This synthetic transport record has a local layout requirement only.
#pragma pack(push, 1)
struct PackedRecord {
    std::uint8_t kind;
    std::uint32_t sequence;
};
#pragma pack(pop)

// Ordinary types after the pop must keep their compiler's natural layout.
struct HostRecord {
    std::uint8_t tag;
    double value;
};
#endif
