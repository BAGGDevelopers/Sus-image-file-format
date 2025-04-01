import random

w = 1028
h = 1028

def generate_sus_file(filename, width=w, height=h):
    with open(filename, "w") as file:
        file.write(f"Width = {width}\nHeight = {height}\n\n")
        file.writelines(
            ", ".join(f"{{{random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)}, 255}}" 
                      for _ in range(width)) + "\n\n" for _ in range(height)
        )

generate_sus_file("random.sus")
print(f"{w} x {h} .SUS file generated!")