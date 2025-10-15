#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include "matching/computer.h"

#ifndef OMIT_DUTCH
#include <swisssystems/dutch.h>
#endif

#ifndef OMIT_BURSTEIN
#include <swisssystems/burstein.h>
#endif

namespace py = pybind11;

PYBIND11_MODULE(matching_computer, m) {
    m.doc() = "Matching computer python bindings";

#ifndef OMIT_BURSTEIN
    py::class_<matching::Computer<swisssystems::burstein::matching_computer::edge_weight>>(m, "ComputerBurstein")
        .def(py::init<typename matching::Computer<swisssystems::burstein::matching_computer::edge_weight>::size_type,
                      const swisssystems::burstein::matching_computer::edge_weight&>())
        .def("size", &matching::Computer<swisssystems::burstein::matching_computer::edge_weight>::size)
        .def("add_vertex", &matching::Computer<swisssystems::burstein::matching_computer::edge_weight>::addVertex)
        .def("set_edge_weight", &matching::Computer<swisssystems::burstein::matching_computer::edge_weight>::setEdgeWeight)
        .def("compute_matching", &matching::Computer<swisssystems::burstein::matching_computer::edge_weight>::computeMatching)
        .def("get_matching", &matching::Computer<swisssystems::burstein::matching_computer::edge_weight>::getMatching);
#endif

#ifndef OMIT_DUTCH
    py::class_<matching::Computer<swisssystems::dutch::validity_matching_computer::edge_weight>>(m, "ComputerDutchValidity")
        .def(py::init<typename matching::Computer<swisssystems::dutch::validity_matching_computer::edge_weight>::size_type,
                      const swisssystems::dutch::validity_matching_computer::edge_weight&>())
        .def("size", &matching::Computer<swisssystems::dutch::validity_matching_computer::edge_weight>::size)
        .def("add_vertex", &matching::Computer<swisssystems::dutch::validity_matching_computer::edge_weight>::addVertex)
        .def("set_edge_weight", &matching::Computer<swisssystems::dutch::validity_matching_computer::edge_weight>::setEdgeWeight)
        .def("compute_matching", &matching::Computer<swisssystems::dutch::validity_matching_computer::edge_weight>::computeMatching)
        .def("get_matching", &matching::Computer<swisssystems::dutch::validity_matching_computer::edge_weight>::getMatching);

    py::class_<matching::Computer<swisssystems::dutch::optimality_matching_computer::edge_weight>>(m, "ComputerDutchOptimality")
        .def(py::init<typename matching::Computer<swisssystems::dutch::optimality_matching_computer::edge_weight>::size_type,
                      const swisssystems::dutch::optimality_matching_computer::edge_weight&>())
        .def("size", &matching::Computer<swisssystems::dutch::optimality_matching_computer::edge_weight>::size)
        .def("add_vertex", &matching::Computer<swisssystems::dutch::optimality_matching_computer::edge_weight>::addVertex)
        .def("set_edge_weight", &matching::Computer<swisssystems::dutch::optimality_matching_computer::edge_weight>::setEdgeWeight)
        .def("compute_matching", &matching::Computer<swisssystems::dutch::optimality_matching_computer::edge_weight>::computeMatching)
        .def("get_matching", &matching::Computer<swisssystems::dutch::optimality_matching_computer::edge_weight>::getMatching);
#endif
}
