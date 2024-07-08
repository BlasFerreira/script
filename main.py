import streamlit as st
import requests
import re
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

def check_url(new_url):
    try:
        response = requests.head(new_url, timeout=100)  # Aumenta el tiempo de espera a 10 segundos
        if response.status_code == 200:
            return new_url, True
        else:
            return new_url, False
    except requests.exceptions.RequestException:
        return f"An error occurred when trying to access {new_url}.", False

def check_images(url):
    # Replace "400*400" with "2048*2048" in the URL
    new_url_base = re.sub(r'_400\*400', '_2048*2048', url)
    _, file_ext = os.path.splitext(new_url_base)

    # Get the timestamp from the URL
    timestamp_match = re.search(r'(\d+).(JPG|jpg)', new_url_base)
    if not timestamp_match:
        raise ValueError("No timestamp found in the URL.")

    urls_to_check = []
    # Loop from 0 to 9999
    for i in range(0, 10000):
        random = f'{i:03d}'
        # Construct the new URL
        new_url = f"{new_url_base[:-8]}{random}{file_ext}"
        urls_to_check.append(new_url)
    
    # Use a ThreadPoolExecutor to check the URLs in parallel
    with ThreadPoolExecutor(max_workers=50) as executor:  # Reduce max_workers to manage load
        futures = {executor.submit(check_url, url) for url in urls_to_check}
        for future in as_completed(futures):
            result = future.result()
            if result:
                url, success = result
                if success:
                    return url

    return None

def main():
    st.title("URL Image Checker")

    # Mostrar la imagen local
    local_image_path = "rat.jpg"
    if os.path.exists(local_image_path):
        st.image(local_image_path, caption="Local Image: rat.jpg", use_column_width=True)
    else:
        st.error("Local image 'rat.jpg' not found.")
    
    url = st.text_input("Enter the URL:", "")
    
    if st.button("Check Images"):
        if url:
            with st.spinner("Checking images, please wait..."):
                result = check_images(url)
            if result:
                st.success(f"Found a valid URL: {result}")
                st.image(result, caption="Valid Image", use_column_width=True)
                st.download_button(
                    label="Download Image",
                    data=requests.get(result).content,
                    file_name=os.path.basename(result),
                    mime="image/jpeg"
                )
            else:
                st.error("Did not find any URLs that returned a 200 status.")
        else:
            st.error("Please enter a URL.")

if __name__ == "__main__":
    main()
