#include <pybind11/pybind11.h>
#include <pybind11/operators.h>
#include <sstream>
#include <bitset>
#include <utility/uinttypes.h>
#include "utility/dynamicuint.h"

namespace py = pybind11;
using namespace utility::uinttypes;

PYBIND11_MODULE(dynamicuint, m) {
    m.doc() = "DynamicUint python bindings";

    py::class_<DynamicUint>(m, "DynamicUint")
        // Constructors
        .def(py::init<>())                                    // empty (zero)
        .def(py::init<std::uintmax_t>())                      // from integer
        .def(py::init<DynamicUint const &>())                 // copy

        // Arithmetic operators
        .def(py::self + py::self)
        .def(py::self - py::self)

        // Arithmetic operators - DynamicUint with std::uintmax_t
        .def("__add__", [](const DynamicUint &a, std::uintmax_t b){ return a + b; })
        .def("__radd__", [](std::uintmax_t a, const DynamicUint &b){ return a + b; })
        .def("__sub__", [](const DynamicUint &a, std::uintmax_t b){ return a - b; })
        .def("__rsub__", [](std::uintmax_t a, const DynamicUint &b){ return a - b; })

        // Bitwise operators (wrap free functions)
        .def("__or__", [](const DynamicUint &a, std::uintmax_t b){ return a | b; })
        .def("__ror__", [](std::uintmax_t a, const DynamicUint &b){ return a | b; })
        .def("__and__", [](const DynamicUint &a, std::uintmax_t b){ return a & b; })
        .def("__rand__", [](std::uintmax_t a, const DynamicUint &b){ return a & b; })

        // Shift operators
        .def("__lshift__", [](const DynamicUint &a, std::size_t n){ return a << n; })
        .def("__rshift__", [](const DynamicUint &a, std::size_t n){ return a >> n; })

        // In-place operators
        .def(py::self += py::self)
        .def(py::self -= py::self)
        .def("__iadd__", [](DynamicUint &a, std::uintmax_t b){ a += b; return a; })
        .def("__isub__", [](DynamicUint &a, std::uintmax_t b){ a -= b; return a; })
        .def("__ior__", [](DynamicUint &a, std::uintmax_t b){ a |= b; return a; })
        .def("__iand__", [](DynamicUint &a, std::uintmax_t b){ a &= b; return a; })
        .def("__ilshift__", [](DynamicUint &a, std::uintmax_t b){ a <<= b; return a; })
        .def("__irshift__", [](DynamicUint &a, std::uintmax_t b){ a >>= b; return a; })

        // Comparisons
        .def(py::self == py::self)
        .def(py::self != py::self)
        .def(py::self < py::self)
        .def(py::self <= py::self)
        .def(py::self > py::self)
        .def(py::self >= py::self)

        // Conversions
        .def("__bool__", [](const DynamicUint &d) { return static_cast<bool>(d); })

        // to_binary purely in the binding
        .def("to_binary", [](const DynamicUint &value) {
            std::ostringstream oss;
            auto v = DynamicUint::const_view(value);
            // iterate from most significant to least
            for (auto it = v.end(); it != v.begin();) {
                --it;
                oss << std::bitset<std::numeric_limits<std::uintmax_t>::digits>(*it);
            }
            std::string result = oss.str();
            auto first_one = result.find('1');
            if (first_one != std::string::npos) {
                return result.substr(first_one);
            }
            return std::string("0");
        })

        // __str__ and __repr__ using the same approach
        .def("__str__", [](const DynamicUint &value) {
            std::ostringstream oss;
            auto v = DynamicUint::const_view(value);
            for (auto it = v.end(); it != v.begin();) {
                --it;
                oss << std::bitset<std::numeric_limits<std::uintmax_t>::digits>(*it);
            }
            std::string result = oss.str();
            auto first_one = result.find('1');
            if (first_one != std::string::npos) {
                return result.substr(first_one);
            }
            return std::string("0");
        })
        .def("__repr__", [](const DynamicUint &value) {
            std::ostringstream oss;
            auto v = DynamicUint::const_view(value);
            for (auto it = v.end(); it != v.begin();) {
                --it;
                oss << std::bitset<std::numeric_limits<std::uintmax_t>::digits>(*it);
            }
            std::string result = oss.str();
            auto first_one = result.find('1');
            if (first_one != std::string::npos) {
                return "<DynamicUint " + result.substr(first_one) + ">";
            }
            return std::string("<DynamicUint 0>");
        })

        // Expose shiftGrow
        .def("shift_grow", &DynamicUint::shiftGrow<std::size_t>);
}
