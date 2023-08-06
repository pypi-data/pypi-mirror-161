mod counter;

use pyo3::prelude::*;


#[pymodule]
fn simple_lib(_py: Python, m: &PyModule) -> PyResult<()> {
    counter::register_child_module(_py, m)?;

    Ok(())
}