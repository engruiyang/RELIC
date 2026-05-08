from core.app_controller import AppController
import time

def main()->int:
    app=AppController(); app.start()
    for i in range(20):
        s=app.tick(100)
        print(f"tick={i+1} stream_alive={s['stream_alive']} sensor_stream_active={s['sensor_stream_active']} attention={s['attention']} attention_age_ms={s['attention_age_ms']} attention_fresh={s['attention_fresh']} attention_seen_once={s['attention_seen_once']} gyro=({s['gyro_x']},{s['gyro_y']},{s['gyro_z']}) gyro_age_ms={s['gyro_age_ms']} gyro_fresh={s['gyro_fresh']} gyro_seen_once={s['gyro_seen_once']} display_data_available={s['display_data_available']} training_data_valid={s['training_data_valid']} control_data_valid={s['control_data_valid']} quality={s['quality']} quality_reasons={s['quality_reasons']} warning_flags={s['warning_flags']} error_flags={s['error_flags']}")
        time.sleep(0.1)
    return 0

if __name__=='__main__':
    raise SystemExit(main())
