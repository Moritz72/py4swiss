#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include "matching/computer.h"
#include <utility/dynamicuint.h>

namespace py = pybind11;

using validity_edge_weight = matching::computer_supporting_value<1>::type::edge_weight;
using optimality_edge_weight = utility::uinttypes::DynamicUint;

PYBIND11_MODULE(matching_computer, m) {
    m.doc() = "Matching computer python bindings";

    py::class_<matching::Computer<validity_edge_weight>>(m, "ComputerDutchValidity")
        .def(py::init<typename matching::Computer<validity_edge_weight>::size_type,
                      const validity_edge_weight&>())
        .def("size", &matching::Computer<validity_edge_weight>::size)
        .def("add_vertex", &matching::Computer<validity_edge_weight>::addVertex)
        .def("set_edge_weight", &matching::Computer<validity_edge_weight>::setEdgeWeight)
        .def("compute_matching", &matching::Computer<validity_edge_weight>::computeMatching)
        .def("get_matching", &matching::Computer<validity_edge_weight>::getMatching);

    py::class_<matching::Computer<optimality_edge_weight>>(m, "ComputerDutchOptimality")
        .def(py::init<typename matching::Computer<optimality_edge_weight>::size_type,
                      const optimality_edge_weight&>())
        .def("size", &matching::Computer<optimality_edge_weight>::size)
        .def("add_vertex", &matching::Computer<optimality_edge_weight>::addVertex)
        .def("set_edge_weight", &matching::Computer<optimality_edge_weight>::setEdgeWeight)
        .def("compute_matching", &matching::Computer<optimality_edge_weight>::computeMatching)
        .def("get_matching", &matching::Computer<optimality_edge_weight>::getMatching);
}