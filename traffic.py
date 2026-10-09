"""Video vehicle tracking and counting, adapted from Samer's local traffic scripts."""
import argparse
import csv
import json
import math
from pathlib import Path
from counting import LineCounter

def parse_line(value):
    try:
        name,coords=value.split(':',1)
        xy=tuple(float(x) for x in coords.split(','))
        if not name or len(xy)!=4 or not all(math.isfinite(x) and 0<=x<=1 for x in xy): raise ValueError
        return name,((xy[0],xy[1]),(xy[2],xy[3]))
    except ValueError as exc:
        raise argparse.ArgumentTypeError('Use NAME:x1,y1,x2,y2 with normalized coordinates in [0,1]') from exc

def main():
    parser=argparse.ArgumentParser(description='Track vehicles and count crossings of finite line segments.')
    parser.add_argument('--video',type=Path,required=True)
    parser.add_argument('--model',default='yolov8n.pt',help='Ultralytics model path or downloadable model name')
    parser.add_argument('--output',type=Path,default=Path('runs/traffic'))
    parser.add_argument('--line',type=parse_line,action='append',help='NAME:x1,y1,x2,y2; repeat for multiple lines')
    parser.add_argument('--conf',type=float,default=0.25)
    parser.add_argument('--max-frames',type=int,default=0,help='0 processes all frames')
    parser.add_argument('--display',action='store_true')
    parser.add_argument('--save-video',action='store_true')
    parser.add_argument('--meters-per-pixel',type=float,help='Experimental constant-scale speed; requires scene calibration')
    args=parser.parse_args()
    if not args.video.is_file(): parser.error('Input video does not exist')
    if not 0<args.conf<=1: parser.error('--conf must be in (0,1]')
    if args.max_frames<0: parser.error('--max-frames must be non-negative')
    if args.meters_per_pixel is not None and (not math.isfinite(args.meters_per_pixel) or args.meters_per_pixel<=0): parser.error('--meters-per-pixel must be positive and finite')
    named=args.line or [('A',((.30,.80),(.08,.62))),('B',((.80,.80),(.58,.62)))]
    if len({n for n,_ in named})!=len(named): parser.error('Line names must be unique')
    if any(a==b for _,(a,b) in named): parser.error('Line endpoints must differ')
    import cv2
    from ultralytics import YOLO
    cap=cv2.VideoCapture(str(args.video))
    if not cap.isOpened(): parser.error('Cannot decode input video')
    fps=cap.get(cv2.CAP_PROP_FPS)
    if not math.isfinite(fps) or fps<=0:
        cap.release(); parser.error('Video must have valid FPS for reproducible timestamps')
    width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    lines={n:((a[0]*width,a[1]*height),(b[0]*width,b[1]*height)) for n,(a,b) in named}
    counter=LineCounter(lines); model=YOLO(args.model)
    args.output.mkdir(parents=True,exist_ok=True)
    writer=None; positions={}; frames=0; observations=0; unique=set(); crossing_events=0
    try:
        if args.save_video:
            writer=cv2.VideoWriter(str(args.output/'annotated.mp4'),cv2.VideoWriter_fourcc(*'mp4v'),fps,(width,height))
            if not writer.isOpened(): raise RuntimeError('Output video writer could not open')
        with (args.output/'crossings.csv').open('w',newline='',encoding='utf-8') as f:
            csv_writer=csv.writer(f); csv_writer.writerow(['frame','video_time_seconds','track_id','class_id','line','experimental_speed_kmh'])
            while args.max_frames==0 or frames<args.max_frames:
                ok,frame=cap.read()
                if not ok: break
                frame_number=frames; frames+=1; timestamp=frame_number/fps
                # Run inference before adding overlays (the original painted lines first).
                result=model.track(frame,persist=True,conf=args.conf,classes=[2,3,5,7],tracker='bytetrack.yaml',verbose=False)[0]
                if result.boxes.id is not None:
                    for box,tid,cls in zip(result.boxes.xyxy.cpu().numpy(),result.boxes.id.cpu().numpy(),result.boxes.cls.cpu().numpy()):
                        tid=int(tid); cls=int(cls); x1,y1,x2,y2=map(int,box); point=((x1+x2)/2,(y1+y2)/2)
                        observations+=1; unique.add(tid); speed=None
                        if args.meters_per_pixel is not None and tid in positions:
                            prev,prev_t=positions[tid]
                            if timestamp>prev_t: speed=math.dist(point,prev)*args.meters_per_pixel/(timestamp-prev_t)*3.6
                        positions[tid]=(point,timestamp)
                        for name in counter.update(tid,point):
                            crossing_events+=1
                            csv_writer.writerow([frame_number,round(timestamp,4),tid,cls,name,'' if speed is None else round(speed,2)])
                        cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),2)
                        label=f'ID {tid}' if speed is None else f'ID {tid} | ~{speed:.1f} km/h (uncalibrated)'
                        cv2.putText(frame,label,(x1,max(15,y1-8)),cv2.FONT_HERSHEY_SIMPLEX,.45,(0,255,0),1)
                for i,(name,(a,b)) in enumerate(lines.items()):
                    cv2.line(frame,tuple(map(int,a)),tuple(map(int,b)),(255,100,0),2)
                    cv2.putText(frame,f'{name}: {counter.counts[name]}',(15,30+i*30),cv2.FONT_HERSHEY_SIMPLEX,.7,(255,100,0),2)
                if writer is not None: writer.write(frame)
                if args.display:
                    cv2.imshow('Vehicle tracking and counting',frame)
                    if cv2.waitKey(1)&0xff in [27,ord('q')]: break
    finally:
        cap.release()
        if writer is not None: writer.release()
        if args.display: cv2.destroyAllWindows()
    summary={'frames_processed':frames,'fps':fps,'tracked_box_observations':observations,'unique_track_ids':len(unique),'line_crossings':counter.counts,'crossing_events':crossing_events,'model':Path(args.model).name,'normalized_lines':dict(named),'speed_enabled':args.meters_per_pixel is not None,'speed_calibration_verified':False,'evaluation':'Execution smoke test only; no ground-truth accuracy evaluation.'}
    (args.output/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))

if __name__=='__main__': main()
