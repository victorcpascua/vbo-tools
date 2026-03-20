import argparse
import sys
import os

from tools import csv2vbo, add_video

def main():
    parser = argparse.ArgumentParser(description="VBO Tools")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # csv2vbo parser
    parser_csv = subparsers.add_parser("csv2vbo", help="Convert CSV data to VBO format")
    parser_csv.add_argument("input_pos", nargs='?', help="Input CSV file (positional)")
    parser_csv.add_argument("-i", "--input", dest="input_opt", help="Input CSV file (option)")
    parser_csv.add_argument("-o", "--output", dest="output_file", help="Output VBO file (optional)")
    parser_csv.add_argument("-v", "--video", dest="video_file", help="Input video file to bundle after conversion (optional)")
    parser_csv.add_argument("-s", "--sync-offset", type=float, default=0.0, dest="offset", help="Time offset in seconds to synchronize video with data (used with -v)")

    # add-video parser
    parser_vid = subparsers.add_parser("add-video", help="Add video synchronization data to a VBO file")
    parser_vid.add_argument("input_data", help="Input VBO file")
    parser_vid.add_argument("video_file", help="Input video file (.mp4 or .avi)")
    parser_vid.add_argument("-s", "--sync-offset", type=float, default=0.0, dest="offset", help="Time offset in seconds to synchronize video with data")

    args = parser.parse_args()

    if args.command == "csv2vbo":
        input_file = args.input_pos or args.input_opt
        if not input_file:
            parser_csv.error("Input file is required. Provide it as a positional argument or using -i/--input.")
            
        ext = os.path.splitext(input_file)[1].lower()
        if ext != '.csv':
            parser_csv.error("Input file must be a .csv file.")

        output_file = args.output_file
        if not output_file:
            output_file = os.path.splitext(input_file)[0] + ".vbo"
            
        try:
            csv2vbo.convert_file(input_file, output_file)
            print(f"Successfully converted {input_file} to {output_file}")
            
            if args.video_file:
                # Add video to the newly converted VBO
                add_video.add_video_to_vbo(output_file, args.video_file, offset=args.offset)
        except Exception as e:
            print("error: %s" % e, file=sys.stderr)
            sys.exit(-1)

    elif args.command == "add-video":
        input_file = args.input_data
        video_file = args.video_file

        # Validate input file extension
        ext = os.path.splitext(input_file)[1].lower()
        if ext != '.vbo':
            parser_vid.error("Input data file must be a .vbo file.")
            
        # Validate video file extension
        vid_ext = os.path.splitext(video_file)[1].lower()
        if vid_ext not in ['.avi', '.mp4']:
            parser_vid.error("Video file must be .avi or .mp4.")
                
        try:
            add_video.add_video_to_vbo(input_file, video_file, offset=args.offset)
        except Exception as e:
            print(f"Error adding video to VBO: {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()
