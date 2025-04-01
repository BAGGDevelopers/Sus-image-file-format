from PIL import Image

def jpg_to_sus(image_path, sus_path):
    try:
        image = Image.open(image_path)
    except IOError:
        print(f"Unable to open image {image_path}")
        return
    
    image = image.convert("RGBA")

    width, height = image.size

    with open(sus_path, 'w') as sus_file:
        
        sus_file.write(f"width={width}\n")
        sus_file.write(f"height={height}\n")
        
        sus_file.write("pixel_data=\n")
        sus_file.write("{\n")
        
        pixels = list(image.getdata())  
        
        for i, pixel in enumerate(pixels):
            if i % width == 0 and i != 0:
                sus_file.write("\n")
            
            sus_file.write(f"{{{pixel[0]}, {pixel[1]}, {pixel[2]}, {pixel[3]}}}")
            
            
            if (i + 1) % width != 0:
                sus_file.write(", ")
            else:
                sus_file.write(" ")
        
        sus_file.write("\n}")
    
    print(f"SUS file saved to {sus_path}")


if __name__ == "__main__":
    input_jpg = "WINDOWICON.jpg"
    
    output_sus = "output_image.sus"
    
    jpg_to_sus(input_jpg, output_sus)
