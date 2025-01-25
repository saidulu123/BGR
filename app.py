import streamlit as st
from rembg import remove
from PIL import Image, UnidentifiedImageError
import tempfile
import os
import io

# Set up Streamlit app configuration
st.set_page_config(page_title="Image Processor", layout="centered")

# Load CSS
st.markdown("""
<style>
body {
    font-family: Arial, sans-serif;
    background-color: #f8f9fa;
    margin: 0;
    padding: 0;
}
.container {
    background: #ffffff;
    padding: 20px 40px;
    border-radius: 8px;
    box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
    width: 100%;
    max-width: 600px;
    margin: auto;
}
h1 {
    color: #333;
    font-size: 24px;
    margin-bottom: 16px;
}
</style>
""", unsafe_allow_html=True)

# App Title
st.markdown("<div class='container'><h1>Image Background Replacement Tool</h1></div>", unsafe_allow_html=True)

# File upload widgets
foreground_file = st.file_uploader("Upload Foreground Image (JPEG/PNG)", type=["jpg", "jpeg", "png"])
background_file = st.file_uploader("Upload Background Image (JPEG/PNG)", type=["jpg", "jpeg", "png"])

# Helper function to process images
def process_images(foreground, background):
    try:
        # Open and resize images
        fg_img = Image.open(foreground).convert("RGBA")
        bg_img = Image.open(background).convert("RGBA")

        # Resize to manageable dimensions if too large
        max_size = 1024
        fg_img.thumbnail((max_size, max_size))
        bg_img.thumbnail(fg_img.size)

        # Remove background
        fg_byte_arr = io.BytesIO()
        fg_img.save(fg_byte_arr, format="PNG")
        processed_data = remove(fg_byte_arr.getvalue(), alpha_matting=True)
        processed_fg_img = Image.open(io.BytesIO(processed_data)).convert("RGBA")

        # Composite images
        composite_img = Image.alpha_composite(bg_img, processed_fg_img)

        return composite_img
    except UnidentifiedImageError:
        st.error("Uploaded file is not a valid image. Please try again.")
        return None
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

# Process images and display results
if foreground_file and background_file:
    with st.spinner("Processing images..."):
        output_image = process_images(foreground_file, background_file)
        if output_image:
            st.image(output_image, caption="Processed Image", use_container_width=True)

            # Provide a download button
            output_buffer = io.BytesIO()
            output_image.save(output_buffer, format="PNG")
            st.download_button(
                label="Download Processed Image",
                data=output_buffer.getvalue(),
                file_name="processed_image.png",
                mime="image/png",
            )
else:
    st.info("Upload both foreground and background images to continue.")
