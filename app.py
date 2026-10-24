"""Start with: python -m streamlit run app.py"""
from pathlib import Path
import tempfile
import streamlit as st
from motionsketch.core import demo_motion, process_motion
from motionsketch.tracking import analyze, download_model, DEFAULT_MODEL
from motionsketch.render import figure, render_frame
from motionsketch.export import export_bundle

st.set_page_config(page_title='MotionSketch',page_icon='◉',layout='wide')
st.title('MotionSketch')
st.caption('Video → approximate human motion → editable 3D data and keyframes')
st.info('Single human, hip-relative motion. No scanned surfaces, animals, furniture, or camera reconstruction. Center of mass is approximate.')
with st.sidebar:
    st.header('Processing')
    sample_fps = st.select_slider('Analyze frames per second',[6,10,12,15,20,24],value=12)
    seconds = st.slider('Maximum clip seconds',5,120,30)
    width = st.select_slider('Inference width',[320,480,640,960],value=640)
    threshold = st.slider('Minimum whole-body confidence',.1,.9,.5,.05)
    st.caption('Lower confidence may recover occluded poses but reduces reliability.')
    output_fps = st.select_slider('Output frames per second',[12,15,24,30],value=24)
    smoothing = st.slider('Follow new motion (1 = no smoothing)',.1,1.,.55,.05)
    st.caption('Interpolation bridges at most 0.20 seconds; longer gaps stay blank.')
    if not DEFAULT_MODEL.exists():
        if st.button('Download human pose model'):
            try:
                with st.spinner('Downloading model from Google…'):
                    download_model()
                st.success('Model ready.')
            except Exception as error:
                st.error(str(error))
    else:
        st.success('Pose model available locally')
    st.caption('Inference runs on this computer. Internet is needed for installation and the model download.')

upload = st.file_uploader('Load a short, single-person clip',type=['mp4','mov','avi','mkv','webm'])
left,right = st.columns(2)
run = left.button('Analyze video',disabled=upload is None,type='primary')
demo = right.button('Try synthetic demo (no model needed)')
if run or demo:
    st.session_state.pop('bundle',None)
    try:
        if demo:
            raw = demo_motion()
        else:
            progress = st.progress(0.,text='Estimating full-body pose…')
            with tempfile.TemporaryDirectory(prefix='motionsketch-input-') as temp:
                path = Path(temp)/('input'+Path(upload.name).suffix)
                path.write_bytes(upload.getbuffer())
                raw = analyze(path,sample_fps=sample_fps,max_width=width,max_seconds=seconds,
                              confidence_threshold=threshold,progress=progress.progress)
                raw.metadata['source'] = upload.name
            progress.empty()
        st.session_state.raw = raw
        st.session_state.pop('frame',None)
    except Exception as error:
        st.session_state.pop('raw',None)
        st.error(f'Processing failed: {error}')

if 'raw' in st.session_state:
    raw = st.session_state.raw
    motion = process_motion(raw,output_fps=output_fps,smoothing=smoothing)
    st.write(f'**{int(motion.valid.sum())} / {len(motion.times)} usable frames** · {motion.times[-1]:.2f} seconds · {raw.metadata["source"]}')
    if raw.metadata.get('truncated'):
        st.warning('Only the configured beginning of the video was processed. Increase the clip limit for more.')
    if not motion.valid.any():
        st.warning('No confident full-body poses found. Use an unobstructed clip showing one person head to toe.')
    view,settings = st.columns([3,1])
    with settings:
        joints = st.checkbox('Show joints',True)
        com = st.checkbox('Show estimated center of mass',True)
        angle = st.slider('Export camera angle',-180,180,25)
        st.caption('Drag the interactive view to rotate it. Export uses the angle above.')
        fmt = st.selectbox('Frame format',['png','jpeg'])
        count = st.slider('Maximum important frames',2,20,8)
        all_frames = st.checkbox('Export every output frame',False)
        st.caption('Important frames prioritize different poses. Filled frames use linear interpolation, not generative AI.')
    with view:
        # Changing the output FPS can shrink the slider domain.
        if st.session_state.get('frame',0) >= len(motion.times):
            st.session_state.frame = 0
        index = st.slider('Frame',0,len(motion.times)-1,0,key='frame') if len(motion.times)>1 else 0
        st.caption(f'{motion.times[index]:.3f}s · {motion.status[index]}')
        st.plotly_chart(figure(motion,index,joints,com),use_container_width=True)
    with st.expander('Rendered export preview'):
        st.image(render_frame(motion,index,joints,com,angle),use_container_width=True)
    if st.button('Build animation and frame export',disabled=not motion.valid.any()):
        try:
            with st.spinner('Rendering animation and packaging frames…'), tempfile.TemporaryDirectory(prefix='motionsketch-export-') as temp:
                archive,warnings = export_bundle(motion,Path(temp)/'result',image_format=fmt,
                                                key_count=count,all_frames=all_frames,
                                                joints=joints,com=com,angle=angle)
                st.session_state.bundle = archive.read_bytes()
            for warning in warnings:
                st.warning(warning)
        except Exception as error:
            st.error(f'Export failed: {error}')
    if 'bundle' in st.session_state:
        st.download_button('Download last built export ZIP',st.session_state.bundle,
                           'motionsketch-export.zip','application/zip')
        st.caption('Rebuild after changing any settings. ZIP contains AVI, motion JSON/CSV, images and a Blender exporter.')
else:
    st.write('Start with the synthetic demo, or download the model and load a video. For best results: one person, full body visible, steady camera, no cuts.')
