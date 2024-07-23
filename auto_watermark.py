import os
from tkinter import *
from tkinter import filedialog
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip

image_extensions = ['.jpg', '.jpeg', '.png']
video_extensions = ['.mp4','.avi', '.mkv', '.mov']
window = Tk()
window.title('Auto Watermark PP')
window.geometry("400x200")
window.config(background = "white")

global image_path, video_path, render_path


label_file_explorer = Label(window, 
							text = "Projeto Auto Warermark - v1 Desktop",
							width = 50, height = 2, 
							fg = "blue")


def browse_image_file():
	global image_path
	data = filedialog.askopenfilename(
										initialdir = os.path.expanduser('~'),
										title = "Selecione o arquivo de imagem",
										filetypes = (
											("Arquivos de imagem", image_extensions),
										))
	image_path =  os.path.abspath(data)

 
def browse_video_file():
	global video_path
	data = filedialog.askopenfilename(
										initialdir = os.path.expanduser('~'),
										title = "Selecione o arquivo de video",
										filetypes = (
											("Arquivos de vídeo", video_extensions),
										))
	video_path =  os.path.abspath(data)
	
 
def destination_folder():
	global render_path
	data = filedialog.askdirectory()
	render_path =  os.path.abspath(data)


button_image_explore = Button(window, 
						text = "Buscar marca d'água",
						command = browse_image_file) 

button_video_explore = Button(window, 
						text = "Buscar vídeo",
						command = browse_video_file) 

button_destination_folder = Button(window, 
						text = "Pasta de destino da renderização",
						command = destination_folder) 

def apply_watermark():
	global image_path, video_path, render_path
	video_name = 'teste'
	video_clip = VideoFileClip(video_path)
	image_clip = ImageClip(image_path)
	image_clip = image_clip.set_duration(video_clip.duration)
	video_with_watermark = CompositeVideoClip([video_clip, image_clip.set_position(('right','top'))])
	render_path = os.path.join(render_path, f"{video_name}_rendered.mp4")
	video_with_watermark.write_videofile(
							render_path,
							codec='libx264', #
							fps=30,
							threads=12,
							ffmpeg_params=['-pix_fmt', 'yuv420p'],  
						)

 
button_apply_watermark = Button(window, 
						text = "Aplicar marca d'agua",
						command = apply_watermark) 

button_exit = Button(window, 
					text = "Sair",
					command = exit) 

label_file_explorer.grid(column = 1, row = 1)
button_image_explore.grid(column = 1, row = 2)
button_video_explore.grid(column = 1, row = 3)
button_destination_folder.grid(column = 1, row = 4)
button_apply_watermark.grid(column = 1, row = 5)
button_exit.grid(column = 1, row= 6)

window.mainloop()
