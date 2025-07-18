use std::ffi::CStr;
use std::os::raw::{c_char, c_int, c_uint};
use image::{imageops::FilterType, GenericImageView, ImageError};

#[inline]
fn get_str_from_ptr(ptr: *const c_char) -> Option<&'static str> {
    if ptr.is_null() {
        return None;
    }
    unsafe {
        CStr::from_ptr(ptr).to_str().ok()
    }
}

#[no_mangle]
pub extern "C" fn resize_jpeg_ffi(
    input_path: *const c_char,
    output_path: *const c_char,
    new_width: c_uint,
    new_height: c_uint,
) -> c_int {
    let (input, output) = match (
        get_str_from_ptr(input_path),
        get_str_from_ptr(output_path),
    ) {
        (Some(i), Some(o)) => (i, o),
        _ => return -1,
    };

    match resize_jpeg(input, output, new_width, new_height) {
        Ok(_) => 0,
        Err(_) => -1,
    }
}

#[no_mangle]
pub extern "C" fn resize_jpeg_percent_ffi(
    input_path: *const c_char,
    output_path: *const c_char,
    percent: c_uint,
) -> c_int {
    let (input, output) = match (
        get_str_from_ptr(input_path),
        get_str_from_ptr(output_path),
    ) {
        (Some(i), Some(o)) => (i, o),
        _ => return -1,
    };

    let img = match image::open(input) {
        Ok(i) => i,
        Err(_) => return -1,
    };

    let (orig_w, orig_h) = img.dimensions();
    let scale = percent as f32 / 100.0;
    let new_w = (orig_w as f32 * scale).round() as u32;
    let new_h = (orig_h as f32 * scale).round() as u32;

    match resize_jpeg(input, output, new_w, new_h) {
        Ok(_) => 0,
        Err(_) => -1,
    }
}

#[no_mangle]
pub extern "C" fn get_jpeg_dimensions_ffi(
    input_path: *const c_char,
    out_width: *mut c_uint,
    out_height: *mut c_uint,
) -> c_int {
    if input_path.is_null() || out_width.is_null() || out_height.is_null() {
        return -1;
    }

    let input = match get_str_from_ptr(input_path) {
        Some(s) => s,
        None => return -1,
    };

    let img = match image::open(input) {
        Ok(i) => i,
        Err(_) => return -1,
    };

    let (w, h) = img.dimensions();
    unsafe {
        *out_width = w;
        *out_height = h;
    }

    0
}

fn resize_jpeg(
    input_path: &str,
    output_path: &str,
    new_width: u32,
    new_height: u32,
) -> Result<(), ImageError> {
    let img = image::open(input_path)?;
    let resized = img.resize(new_width, new_height, FilterType::Lanczos3);
    resized.save(output_path)?;
    Ok(())
}
