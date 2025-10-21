
import pygame
import tkinter as tk
from tkinter import filedialog
from pygame.locals import QUIT, MOUSEBUTTONDOWN
import sys
from PIL import Image


# Default ASCII character sets
CHAR_SETS = {
    'Standard': ['@', '%', '#', '*', '+', '=', '-', ':', '.', ' '],
    'Dense': ['@', '#', 'S', '%', '?', '*', '+', ';', ':', ',', '.'],
    'Sparse': ['#', 'A', 'H', 'O', 'C', ' ', '.', ' '],
    'Blocks': ['█', '▓', '▒', '░', '.', ' '],
}
ASCII_CHARS = CHAR_SETS['Standard']


def image_to_ascii(image_path, width=100):
    img = Image.open(image_path)
    aspect_ratio = img.height / img.width
    new_height = int(aspect_ratio * width * 0.55)
    img = img.resize((width, new_height))
    img = img.convert('L')
    pixels = img.getdata()
    ascii_str = ''
    for i in range(len(pixels)):
        idx = min(pixels[i] * len(ASCII_CHARS) // 256, len(ASCII_CHARS) - 1)
        ascii_str += ASCII_CHARS[idx]
        if (i + 1) % width == 0:
            ascii_str += '\n'
    return ascii_str

def select_image():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        filetypes=[('Image Files', '*.png;*.jpg;*.jpeg;*.bmp;*.gif')]
    )
    return file_path

def draw_button(screen, rect, text, font, color, text_color):
    pygame.draw.rect(screen, color, rect)
    text_surf = font.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)

def main():
    pygame.init()
    screen = pygame.display.set_mode((900, 700))
    pygame.display.set_caption('ASCII Art Converter')
    font = pygame.font.SysFont('Courier', 14)
    button_font = pygame.font.SysFont('Arial', 18)

    usage_text = [
        "ASCII Art Converter",
        "1. Click 'Import Image' to select a picture.",
        "2. Click 'Convert' to generate ASCII art.",
        "3. Click 'Exit' to close the app.",
        "",
        "Tip: Use simple images for best results."
    ]

    import_btn = pygame.Rect(50, 600, 150, 50)
    convert_btn = pygame.Rect(220, 600, 150, 50)
    charset_btns = [pygame.Rect(700, 400 + i*40, 160, 30) for i in range(len(CHAR_SETS))]
    density_minus_btn = pygame.Rect(700, 340, 30, 30)
    density_plus_btn = pygame.Rect(830, 340, 30, 30)
    exit_btn = pygame.Rect(390, 600, 150, 50)

    image_path = None
    ascii_art = None
    status = ""
    preview_img = None
    selected_charset = 'Standard'
    density = 100

    running = True
    need_update_ascii = False
    while running:
        screen.fill((30, 30, 30))

        # Draw usage guide
        y = 20
        for line in usage_text:
            text_surface = font.render(line, True, (200, 200, 200))
            screen.blit(text_surface, (30, y))
            y += 22

        # Draw buttons
        draw_button(screen, import_btn, "Import Image", button_font, (70,130,180), (255,255,255))
        draw_button(screen, convert_btn, "Convert", button_font, (70,180,130), (255,255,255))
        draw_button(screen, exit_btn, "Exit", button_font, (180,70,70), (255,255,255))

        # Draw charset selection
        charset_label = font.render("ASCII Set:", True, (255,255,180))
        screen.blit(charset_label, (700, 380))
        for i, name in enumerate(CHAR_SETS.keys()):
            color = (120,200,120) if name == selected_charset else (80,80,80)
            draw_button(screen, charset_btns[i], name, font, color, (255,255,255))

        # Draw density controls
        density_label = font.render(f"Density: {density}", True, (255,255,180))
        screen.blit(density_label, (700, 320))
        draw_button(screen, density_minus_btn, "-", font, (80,80,80), (255,255,255))
        draw_button(screen, density_plus_btn, "+", font, (80,80,80), (255,255,255))

        # Draw status
        status_surface = font.render(status, True, (255, 220, 120))
        screen.blit(status_surface, (700, 620))

        # Draw image preview if available
        if preview_img:
            img_rect = preview_img.get_rect()
            img_rect.topleft = (700, 180)
            screen.blit(preview_img, img_rect)
            preview_label = font.render("Preview:", True, (255, 255, 180))
            screen.blit(preview_label, (700, 160))

        # Real-time ASCII art preview
        if image_path and need_update_ascii:
            try:
                ASCII_CHARS = CHAR_SETS[selected_charset]
                ascii_art = image_to_ascii(image_path, width=density)
                status = "ASCII art updated."
            except Exception as e:
                ascii_art = None
                status = f"Error: {e}"
            need_update_ascii = False

        # Draw ASCII art if available
        if ascii_art:
            art_lines = ascii_art.split('\n')
            y = 180
            for line in art_lines:
                if y > 580:
                    break
                art_surface = font.render(line, True, (255,255,255))
                screen.blit(art_surface, (30, y))
                y += 12

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == MOUSEBUTTONDOWN:
                if import_btn.collidepoint(event.pos):
                    image_path = select_image()
                    if image_path:
                        status = "Image loaded."
                        # Load and scale preview image
                        try:
                            pil_img = Image.open(image_path)
                            pil_img.thumbnail((160, 120))
                            mode = pil_img.mode
                            size = pil_img.size
                            data = pil_img.tobytes()
                            preview_img = pygame.image.fromstring(data, size, mode)
                        except Exception as e:
                            preview_img = None
                            status = f"Error loading preview: {e}"
                        need_update_ascii = True
                    else:
                        status = "No image selected."
                        preview_img = None
                elif convert_btn.collidepoint(event.pos):
                    if image_path:
                        ASCII_CHARS = CHAR_SETS[selected_charset]
                        ascii_art = image_to_ascii(image_path, width=density)
                        status = "ASCII art generated."
                    else:
                        status = "Please import an image first."
                elif exit_btn.collidepoint(event.pos):
                    running = False
                # Charset selection
                for i, btn in enumerate(charset_btns):
                    if btn.collidepoint(event.pos):
                        selected_charset = list(CHAR_SETS.keys())[i]
                        status = f"Set: {selected_charset}"
                        need_update_ascii = True
                # Density controls
                if density_minus_btn.collidepoint(event.pos):
                    density = max(20, density - 10)
                    need_update_ascii = True
                if density_plus_btn.collidepoint(event.pos):
                    density = min(200, density + 10)
                    need_update_ascii = True

        pygame.display.flip()
    pygame.quit()

if __name__ == '__main__':
    main()
