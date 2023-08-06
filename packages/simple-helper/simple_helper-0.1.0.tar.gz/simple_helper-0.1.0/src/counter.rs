use std::collections::HashMap;
use pyo3::prelude::*;
use pyo3::py_run;

#[pyfunction]
pub fn count_word(data: String) -> HashMap<char, i32> {
    let letter_counts: HashMap<char, i32> = data
        .to_lowercase()
        .chars()
        .fold(HashMap::new(), |mut map, c| {
            *map.entry(c).or_insert(0) += 1;
            map
        });

    letter_counts
}

pub fn register_child_module(py: Python<'_>, parent_module: &PyModule) -> PyResult<()> {
    let string_converter = PyModule::new(py, "string")?;

    string_converter.add_function(wrap_pyfunction!(count_word, parent_module)?)?;

    py_run!(py, string_converter, "import sys; sys.modules['simple_lib.counter'] = string_converter");

    Ok(())
}