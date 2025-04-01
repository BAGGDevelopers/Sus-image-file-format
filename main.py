import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

class SusImageViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("SUS Image Viewer")
        self.root.geometry("800x600")
        
        # Create the canvas to display the image
        self.canvas = tk.Canvas(root, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Create a frame to organize the buttons better
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(pady=10)

        # Load & Save Frame
        self.load_save_frame = tk.Frame(self.button_frame)
        self.load_save_frame.grid(row=0, column=0, padx=10, pady=10)

        self.button_load = tk.Button(self.load_save_frame, text="Load SUS Image", command=self.load_sus_image)
        self.button_load.grid(row=0, column=0, padx=10, pady=5)

        self.button_save_png = tk.Button(self.load_save_frame, text="Save as PNG", command=self.save_image_png)
        self.button_save_png.grid(row=0, column=1, padx=10, pady=5)

        self.button_save_jpg = tk.Button(self.load_save_frame, text="Save as JPG", command=self.save_image_jpg)
        self.button_save_jpg.grid(row=0, column=2, padx=10, pady=5)

        # Convert Frame
        self.convert_frame = tk.Frame(self.button_frame)
        self.convert_frame.grid(row=1, column=0, padx=10, pady=10)

        self.button_convert_png = tk.Button(self.convert_frame, text="Convert to PNG", command=self.convert_to_png)
        self.button_convert_png.grid(row=0, column=0, padx=10, pady=5)

        self.button_convert_jpg = tk.Button(self.convert_frame, text="Convert to JPG", command=self.convert_to_jpg)
        self.button_convert_jpg.grid(row=0, column=1, padx=10, pady=5)

        # Conversion from PNG/JPG to SUS
        self.convert_to_sus_frame = tk.Frame(self.button_frame)
        self.convert_to_sus_frame.grid(row=2, column=0, padx=10, pady=10)

        self.button_convert_png_to_sus = tk.Button(self.convert_to_sus_frame, text="Convert PNG to SUS", command=self.convert_png_to_sus)
        self.button_convert_png_to_sus.grid(row=0, column=0, padx=10, pady=5)

        self.button_convert_jpg_to_sus = tk.Button(self.convert_to_sus_frame, text="Convert JPG to SUS", command=self.convert_jpg_to_sus)
        self.button_convert_jpg_to_sus.grid(row=0, column=1, padx=10, pady=5)

        self.image = None
        self.tk_image = None
        self.img_id = None
        self.zoom_factor = 1.0
        self.offset_x = 0
        self.offset_y = 0

        # Canvas mouse interaction
        self.canvas.bind("<MouseWheel>", self.smooth_zoom)
        self.canvas.bind("<ButtonPress-1>", self.start_pan)
        self.canvas.bind("<B1-Motion>", self.pan)

        # Movement hotkeys
        self.root.bind("<w>", lambda e: self.move_view(0, -20))
        self.root.bind("<s>", lambda e: self.move_view(0, 20))
        self.root.bind("<a>", lambda e: self.move_view(-20, 0))
        self.root.bind("<d>", lambda e: self.move_view(20, 0))
        self.root.bind("<Up>", lambda e: self.move_view(0, -20))
        self.root.bind("<Down>", lambda e: self.move_view(0, 20))
        self.root.bind("<Left>", lambda e: self.move_view(-20, 0))
        self.root.bind("<Right>", lambda e: self.move_view(20, 0))

    def convert_sus_to_image(self, sus_data, width, height):
        image = Image.new("RGBA", (width, height))
        pixels = [tuple(sus_data[i:i+4]) for i in range(0, len(sus_data), 4)]
        image.putdata(pixels)
        return image

    def load_sus_image(self):
        filepath = filedialog.askopenfilename(filetypes=[("SUS Files", "*.sus")])
        if not filepath:
            return

        with open(filepath, "r") as file:
            lines = file.readlines()

        try:
            width = int(lines[0].split('=')[1].strip())
            height = int(lines[1].split('=')[1].strip())
        except (IndexError, ValueError):
            messagebox.showerror("Error", "Invalid SUS file format. Could not read width/height.")
            return

        pixel_data = []
        for line in lines[2:]:  
            line = line.strip().replace('{', '').replace('}', '')  
            if not line:
                continue

            pixel_values = line.split(',')
            cleaned_values = [p.strip() for p in pixel_values if p.strip()]

            try:
                pixel_data.extend(map(int, cleaned_values))
            except ValueError as e:
                print(f"Error processing pixel: {cleaned_values} - {e}")

        expected_length = width * height * 4
        if len(pixel_data) != expected_length:
            messagebox.showerror("Error", f"Pixel data length mismatch. Expected {expected_length}, got {len(pixel_data)}")
            return

        self.image = self.convert_sus_to_image(pixel_data, width, height)
        self.display_image()

    def display_image(self):
        if self.image:
            self.zoom_factor = 1.0
            self.offset_x = 0
            self.offset_y = 0
            self.update_canvas()

    def update_canvas(self):
        if self.image:
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            left = max(0, self.offset_x)
            upper = max(0, self.offset_y)
            right = min(self.image.width, left + int(canvas_width / self.zoom_factor))
            lower = min(self.image.height, upper + int(canvas_height / self.zoom_factor))
            
            if right <= left:
                right = left + 1  
            if lower <= upper:
                lower = upper + 1  

            cropped_image = self.image.crop((left, upper, right, lower))
            new_width = int((right - left) * self.zoom_factor)
            new_height = int((lower - upper) * self.zoom_factor)
            resized_image = cropped_image.resize((new_width, new_height), Image.NEAREST)

            self.tk_image = ImageTk.PhotoImage(resized_image)
            self.canvas.delete("all")
            self.img_id = self.canvas.create_image(canvas_width // 2, canvas_height // 2, image=self.tk_image, anchor=tk.CENTER)

    def smooth_zoom(self, event):
        if self.image:
            zoom_step = 1.1 if event.delta > 0 else 0.9
            new_zoom = self.zoom_factor * zoom_step

            if new_zoom < 1.0:
                return

            x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
            rel_x = (x - self.offset_x) / self.zoom_factor
            rel_y = (y - self.offset_y) / self.zoom_factor

            self.zoom_factor = new_zoom
            self.offset_x = x - rel_x * new_zoom
            self.offset_y = y - rel_y * new_zoom

            self.update_canvas()

    def start_pan(self, event):
        self.pan_start_x = event.x
        self.pan_start_y = event.y

    def pan(self, event):
        dx = (event.x - self.pan_start_x) / self.zoom_factor
        dy = (event.y - self.pan_start_y) / self.zoom_factor
        self.offset_x -= dx
        self.offset_y -= dy
        self.pan_start_x = event.x
        self.pan_start_y = event.y
        self.update_canvas()

    def move_view(self, dx, dy):
        self.offset_x += dx
        self.offset_y += dy
        self.update_canvas()

    def save_image_png(self):
        if self.image:
            save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Files", "*.png")])
            if save_path:
                self.image.save(save_path)
                messagebox.showinfo("Success", f"Image saved as PNG at {save_path}")

    def save_image_jpg(self):
        if self.image:
            save_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG Files", "*.jpg")])
            if save_path:
                self.image.convert("RGB").save(save_path, "JPEG")
                messagebox.showinfo("Success", f"Image saved as JPG at {save_path}")

    def convert_to_png(self):
        if self.image:
            save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Files", "*.png")])
            if save_path:
                self.image.save(save_path, "PNG")
                messagebox.showinfo("Success", f"Image converted to PNG and saved at {save_path}")

    def convert_to_jpg(self):
        if self.image:
            save_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG Files", "*.jpg")])
            if save_path:
                self.image.convert("RGB").save(save_path, "JPEG")
                messagebox.showinfo("Success", f"Image converted to JPG and saved at {save_path}")

    def convert_png_to_sus(self):
        filepath = filedialog.askopenfilename(filetypes=[("PNG Files", "*.png")])
        if not filepath:
            return

        try:
            image = Image.open(filepath)
            image = image.convert("RGBA")
            width, height = image.size
            sus_data = []

            for pixel in image.getdata():
                sus_data.append(f"{{{pixel[0]}, {pixel[1]}, {pixel[2]}, {pixel[3]}}}")

            sus_filename = filedialog.asksaveasfilename(defaultextension=".sus", filetypes=[("SUS Files", "*.sus")])
            if sus_filename:
                with open(sus_filename, "w") as file:
                    file.write(f"Width = {width}\nHeight = {height}\n\n")
                    for i in range(0, len(sus_data), 10):
                        file.write(", ".join(sus_data[i:i+10]) + "\n")
                messagebox.showinfo("Success", f"PNG converted to SUS and saved at {sus_filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to convert PNG to SUS: {e}")

    def convert_jpg_to_sus(self):
        filepath = filedialog.askopenfilename(filetypes=[("JPEG Files", "*.jpg")])
        if not filepath:
            return

        try:
            image = Image.open(filepath)
            image = image.convert("RGBA")
            width, height = image.size
            sus_data = []

            for pixel in image.getdata():
                sus_data.append(f"{{{pixel[0]}, {pixel[1]}, {pixel[2]}, {pixel[3]}}}")

            sus_filename = filedialog.asksaveasfilename(defaultextension=".sus", filetypes=[("SUS Files", "*.sus")])
            if sus_filename:
                with open(sus_filename, "w") as file:
                    file.write(f"Width = {width}\nHeight = {height}\n\n")
                    for i in range(0, len(sus_data), 10):
                        file.write(", ".join(sus_data[i:i+10]) + "\n")
                messagebox.showinfo("Success", f"JPG converted to SUS and saved at {sus_filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to convert JPG to SUS: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SusImageViewer(root)
    root.mainloop()
