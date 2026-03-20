import sys
import os
import shutil

def add_video_to_vbo(vbo_path, video_path, offset=0.0, trim_start=0.0, trim_end=0.0):
    if not os.path.exists(vbo_path):
        print("Error: VBO file not found.")
        return

    if not os.path.exists(video_path):
        print("Error: Video file not found: " + video_path)
        return

    base_name = os.path.splitext(os.path.basename(vbo_path))[0]
    prefix = f"{base_name}_vid"

    # Output in the SAME folder as the original VBO
    out_dir = os.path.dirname(os.path.abspath(vbo_path))
    
    # Define structure paths: name is {prefix}.vbo (122_vid.vbo)
    vbo_out = os.path.join(out_dir, f"{prefix}.vbo")
    
    # The video is named {prefix}0001.{ext}
    video_ext = os.path.splitext(video_path)[1].lstrip('.').upper()
    if not video_ext: video_ext = 'AVI'
    
    vid_out = os.path.join(out_dir, f"{prefix}0001.{video_ext}")
    
    print(f"Creating VBO with video sync at: {vbo_out}")
    if os.path.abspath(video_path) != os.path.abspath(vid_out):
        video_dir = os.path.dirname(os.path.abspath(video_path))
        if video_dir == out_dir:
            print(f"Renaming video {os.path.basename(video_path)} -> {os.path.basename(vid_out)}")
            os.rename(video_path, vid_out)
        else:
            print(f"Copying video {os.path.basename(video_path)} -> {vid_out}")
            shutil.copy2(video_path, vid_out)

    with open(vbo_path, 'r', encoding='latin-1') as f:
        lines = f.readlines()

    out_lines = []
    section = None
    header_modified = False
    time_index = -1
    
    pre_data_lines = []
    data_lines = []
    data_seconds = []
    post_data_lines = []
    
    i = 0
    in_data = False
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith('['):
            section = stripped
            if section == '[data]':
                in_data = True
                pre_data_lines.append(line)
            elif section == '[column names]':
                pre_data_lines.append("[avi]\n")
                pre_data_lines.append(f"{prefix}\n")
                pre_data_lines.append(f"{video_ext}\n")
                pre_data_lines.append("\n")
                pre_data_lines.append(line)
            else:
                if in_data:
                    in_data = False
                    post_data_lines.append(line)
                else:
                    pre_data_lines.append(line)
        else:
            if section == '[column names]':
                if stripped:
                    cols = stripped.split()
                    try:
                        time_index = cols.index('time')
                    except ValueError:
                        print("Error: Could not find 'time' column in [column names].")
                        return
                    
                    new_cols = cols + ['avifileindex', 'avisynctime']
                    pre_data_lines.append(" ".join(new_cols) + "\n")
                else:
                    pre_data_lines.append(line)
                    
            elif section == '[header]':
                if not stripped and not header_modified:
                    pre_data_lines.append("avifileindex\n")
                    pre_data_lines.append("avisynctime\n")
                    header_modified = True
                pre_data_lines.append(line)
                
            elif section == '[data]':
                if stripped:
                    parts = stripped.split()
                    if time_index != -1 and time_index < len(parts):
                        time_str = parts[time_index]
                        try:
                            # Time format can be seconds or HHMMSS.ms UTC time
                            time_parts = time_str.split('.')
                            if len(time_parts[0]) == 5 or len(time_parts[0]) == 6:
                                time_str_padded = time_parts[0].zfill(6)
                                hh = int(time_str_padded[0:2])
                                mm = int(time_str_padded[2:4])
                                ss = int(time_str_padded[4:6])
                                fraction = float("0." + time_parts[1]) if len(time_parts) > 1 else 0.0
                                total_seconds = hh * 3600 + mm * 60 + ss + fraction
                            else:
                                total_seconds = float(time_str)
                                
                            sync_time_ms = int(round((total_seconds + offset) * 1000.0))
                            
                            avifileindex = "0001"
                            avisynctime = f"{sync_time_ms:08d}"
                            
                            parts.append(avifileindex)
                            parts.append(avisynctime)
                            
                            data_lines.append(" ".join(parts) + "\n")
                            data_seconds.append(total_seconds)
                        except ValueError:
                            parts.append("0001")
                            parts.append("00000000")
                            data_lines.append(" ".join(parts) + "\n")
                            data_seconds.append(None)
                    else:
                        data_lines.append(line)
                        data_seconds.append(None)
                else:
                    data_lines.append(line)
                    data_seconds.append(None)
            else:
                if in_data:
                    post_data_lines.append(line)
                else:
                    pre_data_lines.append(line)
                
        i += 1
        
    # Apply trimming logic
    if len(data_seconds) > 0 and (trim_start > 0 or trim_end > 0):
        valid_seconds = [s for s in data_seconds if s is not None]
        if valid_seconds:
            min_sec = valid_seconds[0] + trim_start
            max_sec = valid_seconds[-1] - trim_end
            
            trimmed_data_lines = []
            for line, sec in zip(data_lines, data_seconds):
                if sec is None or (min_sec <= sec <= max_sec):
                    trimmed_data_lines.append(line)
            data_lines = trimmed_data_lines

    out_lines = pre_data_lines + data_lines + post_data_lines

    with open(vbo_out, 'w', encoding='latin-1') as f:
        f.writelines(out_lines)
        
    print(f"Successfully generated {vbo_out}.")
