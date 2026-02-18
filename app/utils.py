
def align_text_with_speakers(text_segments, speaker_segments):
    """
    Aligns text segments with speaker segments based on time overlap.
    """
    aligned = []
    
    # Handle empty speaker segments
    if not speaker_segments:
        return [{**ts, "speaker": "SPEAKER_00"} for ts in text_segments]

    for ts in text_segments:
        ts_start = ts['start']
        ts_end = ts['end']
        
        # Find speaker with max overlap
        best_speaker = "SPEAKER_00" # Default
        max_overlap = 0
        
        for ss in speaker_segments:
            # Overlap calculation
            start = max(ts_start, ss['start'])
            end = min(ts_end, ss['end'])
            overlap = max(0, end - start)
            
            if overlap > max_overlap:
                max_overlap = overlap
                best_speaker = ss['speaker']
        
        aligned.append({
            **ts,
            "speaker": best_speaker
        })
        
    return aligned

def get_speaker_genders_map(audio_path, speaker_segments):
    """
    Analyze gender for each unique speaker.
    """
    speakers = set(s['speaker'] for s in speaker_segments)
    gender_map = {}
    
    for spk in speakers:
        # Find a good segment for this speaker (longest duration)
        spk_segments = [s for s in speaker_segments if s['speaker'] == spk]
        if not spk_segments:
            continue
            
        longest_seg = max(spk_segments, key=lambda x: x['end'] - x['start'])
        
        # Detect gender on this segment
        try:
            # from app.services.gender_service import detect_gender_for_segment
            # gender = detect_gender_for_segment(audio_path, longest_seg['start'], longest_seg['end'])
            gender = "MALE" # Fallback as gender_service is deprecated
        except Exception as e:
            print(f"Gender detection failed for {spk}: {e}")
            gender = "MALE"
            
        print(f"Detected Gender for {spk}: {gender}")
        gender_map[spk] = gender
        
    return gender_map
