import os
import shutil
import textile
from pathlib import Path
import templ8.programstate
from templ8.blessing import makedir
from templ8.blessing import mod_replaces
from templ8.blessing import full_parse
import time

# Divines a website
def divine(force=False):
	# Load the state of the program (important files and stuff)
	state = templ8.programstate.ProgramState()
	last_change_list = {}
	new_change_list = {}
	if os.path.exists(".chlistd"):
		for i in open(".chlistd", "r", encoding="utf-8").readlines():
			spl = i.split("<<")
			if len(spl) != 2:
				continue
			last_change_list[Path(spl[0])] = float(spl[1])
			new_change_list[Path(spl[0])] = float(spl[1])
	
	finalprint = ""
	for subdir, dirs, files in os.walk(state.input_folder):
		# Copy all the folders in case they're not there yet
		for dir in dirs:
			path = os.path.join(subdir, dir).replace(state.input_folder, state.output_folder, 1)
			makedir(path)
		
		dir_replace = {}
		dirpl8_ch = False
		# Find a global repl8ce thing
		if "repl8ce" in files:
			path = Path(os.path.join(subdir, "repl8ce"))
			mod_replaces(dir_replace, open(path, "r", encoding="utf-8").read())
			if path in last_change_list:
				if last_change_list[path] != os.stat(path).st_mtime:
					new_change_list[path] = os.stat(path).st_mtime
					dirpl8_ch = True
			else:
				new_change_list[path] = os.stat(path).st_mtime
					
		# Process the files
		for file in files:
			path = os.path.join(subdir, file)
			file_extension = os.path.splitext(path)[1]
			outpath = path.replace(state.input_folder, state.output_folder, 1)
			outhtml = outpath.replace(file_extension, ".html", -1)
			
			# Only process textile and md files
			if file_extension in [".textile", ".md", ".km"]:
				current_content = ""
				if os.path.exists(outhtml):
					current_content = open(outhtml, "r", encoding="utf-8").read()
						
				contents = ""
				# Get the headers and the content
				file_split = open(path, "r", encoding="utf-8").read().split("-BEGINFILE-",1)
				file_headers = ""
				file_content = ""
				if len(file_split) >= 2:
					file_headers = file_split[0]
					file_content = file_split[1]
				elif len(file_split) == 1:
					file_headers = ""
					file_content = file_split[0]
				else:
					raise Exception("Issue regarding -BEGINFILE- markers.")
				
				# Check if the folder is in txignore
				in_txignore = False
				for i in state.txignore:
					if os.path.join(state.input_folder, os.path.normpath(i)) == path or os.path.join(state.input_folder, os.path.normpath(i)) == subdir:
						in_txignore = True
						break
					
				
				if not in_txignore:
					npath = Path(path)
					origin_last_time = os.stat(npath).st_mtime
					recorded_last_time = -1
					if npath in last_change_list:
						recorded_last_time = last_change_list[npath]
					
					temp = state.replacements.copy()
					temp.update(dir_replace)
					mod_replaces(temp, file_headers)
					cbasech = False
					
					cbkpath = Path(state.basehtml_path)
					if "CUSTOMBASE" in temp:
						cbkpath = Path(temp["CUSTOMBASE"])
						
					if os.path.exists(cbkpath):
						if cbkpath in last_change_list:
							if last_change_list[cbkpath] != os.stat(cbkpath).st_mtime:
								new_change_list[cbkpath] = os.stat(cbkpath).st_mtime
								cbasech = True
						else:
							new_change_list[cbkpath] = os.stat(cbkpath).st_mtime
							cbasech = True
								
					if recorded_last_time != origin_last_time or cbasech or dirpl8_ch or force:
						contents = full_parse(state, file_content, file_extension, file_headers, dir_replace)
						new_change_list[npath] = origin_last_time
					else:
						continue
					
					if os.path.exists(outhtml):
						contents = contents.replace("#!CDATE!#", time.ctime(os.path.getctime(outhtml)))
					else:
						contents = contents.replace("#!CDATE!#", time.ctime(time.time()))
										
					finalprint += outhtml + "\n"
					with open(outhtml, "w", encoding="utf-8") as f:
						f.write(contents)
					
					
				else:
					finalprint += outpath + "\n"
					with open(outpath, "w", encoding="utf-8") as f:
						f.write(file_content)
					
			else:
				if os.path.exists(outpath):
					if open(path, "rb").read() == open(outpath, "rb").read():
						continue
				finalprint += outpath + "\n"
				shutil.copy(path, outpath)
		
	
	new_change_text = ""
	for p in new_change_list:
		new_change_text += f"{p}<<{new_change_list[p]}\n"
	open(".chlistd", "w", encoding="utf-8").write(new_change_text)
	
	print(finalprint)

	print("Finished assembling")
