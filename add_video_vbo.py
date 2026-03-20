import sys
import os
import shutil

def add_video_to_vbo(vbo_path, video_path):
    if not os.path.exists(vbo_path):
        print("Error: VBO file not found.")
        return

    if not os.path.exists(video_path):
        print("Error: Video file not found: " + video_path)
        return

    base_name = os.path.splitext(os.path.basename(vbo_path))[0]
    prefix = f"{base_name}_vid"

    # Create folder to match VBO Editor's layout
    folder_path = os.path.join(os.path.dirname(os.path.abspath(vbo_path)), prefix)
    os.makedirs(folder_path, exist_ok=True)
    
    # Define structure paths
    vbo_out = os.path.join(folder_path, f"{prefix}Data.vbo")
    
    video_ext = os.path.splitext(video_path)[1].lstrip('.').upper()
    if not video_ext: video_ext = 'AVI'
    
    vid_out = os.path.join(folder_path, f"{prefix}0001.{video_ext}")
    
    print(f"Bundling to {folder_path} ...")
    if os.path.abspath(video_path) != os.path.abspath(vid_out):
        shutil.copy2(video_path, vid_out)

    with open(vbo_path, 'r', encoding='latin-1') as f:
        lines = f.readlines()

    out_lines = []
    section = None
    header_modified = False
    time_index = -1
    
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith('['):
            section = stripped
            if section == '[column names]':
                out_lines.append("[avi]\n")
                out_lines.append(f"{prefix}\n")
                out_lines.append(f"{video_ext}\n")
                out_lines.append("\n")
                
                out_lines.append(line)
            else:
                out_lines.append(line)
        else:
            if section == '[header]':
                if not stripped and not header_modified:
                    out_lines.append("avifileindex\n")
                    out_lines.append("avisynctime\n")
                    header_modified = True
                out_lines.append(line)
                
            elif section == '[column names]':
                if stripped:
                    cols = stripped.split()
                    try:
                        time_index = cols.index('time')
                    except ValueError:
                        print("Error: Could not find 'time' column in [column names].")
                        return
                    
                    new_cols = cols + ['avifileindex', 'avisynctime']
                    out_lines.append(" ".join(new_cols) + "\n")
                else:
                    out_lines.append(line)
                    
            elif section == '[data]':
                if stripped:
                    parts = stripped.split()
                    if time_index != -1 and time_index < len(parts):
                        time_str = parts[time_index]
                        try:
                            time_val = float(time_str)
                            if time_val > 100000:
                                hh = int(time_val / 10000)
                                mm = int((time_val - hh * 10000) / 100)
                                ss = time_val - hh * 10000 - mm * 100
                                total_seconds = hh * 3600 + mm * 60 + ss
                            else:
                                total_seconds = time_val
                                
                            sync_time_ms = int(round(total_seconds * 1000.0))
                            
                            avifileindex = "0001"
                            avisynctime = f"{sync_time_ms:08d}"
                            
                            parts.append(avifileindex)
                            parts.append(avisynctime)
                            
                            out_lines.append(" ".join(parts) + "\n")
                        except ValueError:
                            parts.append("0001")
                            parts.append("00000000")
                            out_lines.append(" ".join(parts) + "\n")
                    else:
                        out_lines.append(line)
                else:
                    out_lines.append(line)
                    
            else:
                out_lines.append(line)
                
        i += 1

    with open(vbo_out, 'w', encoding='latin-1') as f:
        f.writelines(out_lines)
        
    print(f"Successfully generated {vbo_out} bundle.")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python add_video_vbo.py <vbo_in> <video_file>")
        sys.exit(1)
        
    add_video_to_vbo(sys.argv[1], sys.argv[2])
