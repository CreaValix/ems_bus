#include <Python.h>

#include "ems_serio.h"

static PyObject *py_logger;

static PyObject *ems_serio_start(PyObject *self, PyObject *args) {
    char *serial_path;
    int res;

    if (!PyArg_ParseTuple(args, "s", &serial_path)) {
        res = -1;
        goto end;
    }

    res = start(serial_path);

end:
    return(PyLong_FromLong(res));
}

static PyObject *ems_serio_stop(PyObject *self, PyObject *args) {
    int res = stop();

    return(PyLong_FromLong(res));
}

typedef enum {
    NOTSET = 0,
    DEBUG = 10,
    INFO = 20,
    WARNING = 30,
    ERROR = 40,
    CRITICAL = 50,
} logging_level_e;
void ems_serio_log(int level, char* fmt, ...) {
    char msg[128];
    // https://gist.github.com/machinaut/f35ffea92a16c2b44cff4e9ac55678af
    PyGILState_STATE state = PyGILState_Ensure();
    int py_level = level & LOG_ERROR ? ERROR : (level & LOG_INFO ? INFO : DEBUG);

    va_list(args);
    va_start(args, fmt);
    vsnprintf(msg, sizeof(msg), fmt, args);
    va_end(args);

    PyObject_CallMethod(py_logger, "log", "is", py_level, msg);

    PyGILState_Release(state);
}

static PyObject *ems_serio_stats() {
    PyObject *dict;

    // Todo: Check if this is a memory leak and Py_DECREF must be used.
    dict = PyDict_New();
    PyDict_SetItemString(dict, "rx_sync_errors", PyLong_FromUnsignedLong(stats.rx_mac_errors));
    PyDict_SetItemString(dict, "rx_total", PyLong_FromUnsignedLong(stats.rx_total));
    PyDict_SetItemString(dict, "rx_success", PyLong_FromUnsignedLong(stats.rx_success));
    PyDict_SetItemString(dict, "rx_short", PyLong_FromUnsignedLong(stats.rx_short));
    PyDict_SetItemString(dict, "rx_sender", PyLong_FromUnsignedLong(stats.rx_sender));
    PyDict_SetItemString(dict, "rx_format", PyLong_FromUnsignedLong(stats.rx_format));
    PyDict_SetItemString(dict, "tx_total", PyLong_FromUnsignedLong(stats.tx_total));
    PyDict_SetItemString(dict, "tx_fail", PyLong_FromUnsignedLong(stats.tx_fail));
    PyDict_SetItemString(dict, "logging", PyLong_FromUnsignedLong(logging));
    PyDict_SetItemString(dict, "running", PyLong_FromUnsignedLong(!!readloop));
    return(dict);
}

static PyObject *ems_serio_loglevel(PyObject *self, PyObject *args) {
    if (!PyArg_ParseTuple(args, "i", &logging)) {
    return(PyLong_FromLong(-1));
    }

    // Disable logging if the logging module would block it anyway
    PyObject *py_level = PyObject_CallMethod(py_logger, "getEffectiveLevel", "");
    long log_level = PyLong_AsLong(py_level);
    if (log_level > 10) {
        logging &= ~(LOG_VERBOSE | LOG_PACKET | LOG_MAC | LOG_CHAR);
        if (log_level > 20) {
            logging &= ~LOG_INFO;
            if (log_level > 40) {
                logging &= ~LOG_ERROR;
            }
        }
    }
    Py_DECREF(py_level);
    return(PyLong_FromLong(logging));
}


static PyMethodDef module_methods[] = {
    {"start", ems_serio_start, METH_VARARGS, "Starts the EMS serial bus driver"},
    {"stop", ems_serio_stop, METH_VARARGS, "Stops the EMS serial bus driver"},
    {"stats", ems_serio_stats, METH_VARARGS, "Returns a dict of bus statistics"},
    {"loglevel", ems_serio_loglevel, METH_VARARGS, "Sets the internal log level"},
    {NULL, NULL, 0, NULL}
};
static struct PyModuleDef ems_serio = {
    PyModuleDef_HEAD_INIT,
    "ems_serio",
    "EMS serial bus driver",
    -1,
    module_methods
};

PyMODINIT_FUNC PyInit_ems_serio(void) {
    PyObject *module;

    module = PyModule_Create(&ems_serio);
    if (!module) {
        return(NULL);
    }

    PyObject *logging_module = PyImport_ImportModule("logging");
    if (logging_module == NULL) {
        PyErr_SetString(PyExc_ImportError, "Failed to import 'logging' module");
        goto abort;
    }
    py_logger = PyObject_CallMethod(logging_module, "getLogger", "s", "ems_serio");
    if (py_logger == NULL) {
        PyErr_SetString(PyExc_ImportError, "Failed get logger 'ems_serio'");
        goto abort;
    }

    if (PyModule_AddStringConstant(module, "version", "1.0.0") ||
            PyModule_AddIntConstant(module, "LOG_ERROR", LOG_ERROR) ||
            PyModule_AddIntConstant(module, "LOG_INFO", LOG_INFO) ||
            PyModule_AddIntConstant(module, "LOG_VERBOSE", LOG_VERBOSE) ||
            PyModule_AddIntConstant(module, "LOG_PACKET", LOG_PACKET) ||
            PyModule_AddIntConstant(module, "LOG_MAC", LOG_MAC) ||
            PyModule_AddIntConstant(module, "LOG_ERROR", LOG_ERROR) ||
            PyModule_AddIntConstant(module, "LOG_CHAR", LOG_CHAR)) {
        goto abort;
    }

    logging = LOG_INFO | LOG_ERROR;
    goto good;

abort:
    Py_DECREF(module);
    module = NULL;
good:
    return(module);
}
