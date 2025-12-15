#ifndef MATCHINGTEMPLATEINSTANTIATION_H
#define MATCHINGTEMPLATEINSTANTIATION_H

#include <matching/computer.h>
#include <utility/dynamicuint.h>

using validity_edge_weight = matching::computer_supporting_value<1>::type::edge_weight;
using optimality_edge_weight = utility::uinttypes::DynamicUint;

// This macro is called in the cpp files of the matching code to instantiate the
// templates needed for the Swiss systems.

#define INSTANTIATE_MATCHING_EDGE_WEIGHT_TEMPLATES(a) \
    a(validity_edge_weight) \
    a(optimality_edge_weight)

#endif