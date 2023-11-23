import tkinter as tk
from tkinter import filedialog
from PIL import Image


class XORSteganographyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("XOR Steganography")

        self.image_path = tk.StringVar()
        self.message_entry = tk.Entry(root, width=40)
        self.output_label = tk.Label(root, text="")

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Select Image:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        tk.Entry(self.root, textvariable=self.image_path, state='readonly', width=40).grid(row=0, column=1, padx=10,
                                                                                           pady=5)
        tk.Button(self.root, text="Browse", command=self.browse_image).grid(row=0, column=2, padx=10, pady=5)

        tk.Label(self.root, text="Enter Message:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.message_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Button(self.root, text="Embed Message", command=self.embed_message).grid(row=2, column=1, pady=10)
        tk.Button(self.root, text="Extract Message", command=self.extract_message).grid(row=3, column=1, pady=10)

        self.output_label.grid(row=4, column=1)

    def browse_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp")])
        if file_path:
            self.image_path.set(file_path)

    def embed_message(self):
        image_path = self.image_path.get()
        message = self.message_entry.get()

        if not image_path:
            self.output_label.config(text="Please select an image.", fg="red")
            return

        if not message:
            self.output_label.config(text="Please enter a message.", fg="red")
            return

        output_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])

        if not output_path:
            return  # User canceled the save dialog

        try:
            self.embed_text(image_path, message, output_path)
            self.output_label.config(text="Message embedded successfully!", fg="green")
        except Exception as e:
            self.output_label.config(text=f"Error: {str(e)}", fg="red")

    def extract_message(self):
        image_path = self.image_path.get()

        if not image_path:
            self.output_label.config(text="Please select an image.", fg="red")
            return

        try:
            extracted_message = self.extract_text(image_path)
            self.output_label.config(text=f"Extracted Message: {extracted_message}", fg="green")
            print(extracted_message)
        except UnicodeDecodeError as e:
            self.output_label.config(text=f"Error decoding the text: {e}", fg="red")
        except Exception as e:
            self.output_label.config(text=f"Error: {str(e)}", fg="red")

    def embed_text(self, image_path, text, output_path):
        # Convert the input text into a binary string, appending "(end)" to signal the end of the text.
        binary_message = ''.join(format(ord(char), '08b') for char in text + "(end)")

        # Open the input image and get its dimensions and number of color channels.
        image = Image.open(image_path)
        w, h = image.size
        num_channels = len(image.getbands())

        # Calculate the maximum number of characters that can be embedded in the image.
        eN = (h * w * 3) // 8

        # Check if the text is too long to fit in the image.
        if len(text) > eN:
            raise ValueError("Message too long to fit in the image")

        # Iterate over each pixel in the image to embed the binary message.
        message_index = 0
        for i in range(h):
            for j in range(w):
                pixel = list(image.getpixel((j, i)))

                # Skip pixels that are fully transparent in RGBA images.
                if num_channels == 4 and 0 in pixel:
                    continue

                # Embed bits of the message into the RGB channels of the pixel.
                for k in range(3):
                    if message_index < len(binary_message):
                        M = int(binary_message[message_index])
                        pixel[k] = self.xor_substitution(pixel[k], M)
                        message_index += 1
                    else:
                        break

                # Update the pixel with the new values.
                image.putpixel((j, i), tuple(pixel[:num_channels]))

        # Save the modified image to the specified output path.
        image.save(output_path)

    def xor_substitution(self, pixel_value, bit):
        # Convert pixel value to an 8-bit binary string.
        binary_value = format(pixel_value, '08b')

        # Perform XOR operation on the 7th bit of the pixel and the message bit, then replace the last bit.
        modified_binary = binary_value[:7] + str(int(binary_value[6]) ^ bit)

        # Convert the modified binary string back to an integer.
        return int(modified_binary, 2)

    def extract_text(self, image_path):
        # Binary string representing the end marker "(end)".
        end_marker = "0010100001100101011011100110010000101001"

        # Open the image and get its dimensions and number of color channels.
        image = Image.open(image_path)
        w, h = image.size
        num_channels = len(image.getbands())

        # Initialize a list to hold the extracted bits of the message.
        message_bits = []

        # Iterate over each pixel in the image to extract the embedded message.
        for i in range(h):
            for j in range(w):
                pixel = list(image.getpixel((j, i)))

                # Skip pixels that are fully transparent in RGBA images.
                if num_channels == 4 and 0 in pixel:
                    continue

                # Extract the embedded bits from the RGB channels of the pixel.
                for k in range(3):
                    p7, p8 = (pixel[k] >> 1) & 1, pixel[k] & 1
                    message_bits.append(1 if p7 ^ 1 == p8 else 0)

                # Join the bits to form a binary string and check for the end marker.
                message = ''.join(map(str, message_bits))
                if end_marker in message:
                    # Return the extracted text up to the end marker.
                    return self.binary_to_text(message[:-len(end_marker)]).strip()

        # Convert the extracted binary string to text and return it.
        return self.binary_to_text(''.join(map(str, message_bits)))

    def binary_to_text(self, binary_message):
        # Convert a binary string to its corresponding text.
        text = ''
        for i in range(0, len(binary_message), 8):
            byte = binary_message[i:i + 8]
            text += chr(int(byte, 2))
        return text


if __name__ == "__main__":
    root = tk.Tk()
    app = XORSteganographyGUI(root)
    root.mainloop()
