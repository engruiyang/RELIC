from core.app_controller import AppController
import time

def main()->int:
    app=AppController(); app.start()
    for i in range(20):
        s=app.tick(100)
        print(f"tick={i+1} connected={s['device_connected']} bridge_alive={s['bridge_alive']} stream={s['stream_alive']} sensor_stream_active={s['sensor_stream_active']} training_data_valid={s['training_data_valid']} attention={s['attention']} attention_seen_once={s['attention_seen_once']} attention_age_ms={s['attention_age_ms']} focus=({s['focus_x']},{s['focus_y']}) focus_seen_once={s['focus_seen_once']} focus_age_ms={s['focus_age_ms']} gyro=({s['gyro_x']},{s['gyro_y']},{s['gyro_z']}) gyro_seen_once={s['gyro_seen_once']} gyro_age_ms={s['gyro_age_ms']} last_algorithm_age_ms={s['last_algorithm_age_ms']} sqi={s['sqi']:.2f} quality={s['quality']} reasons={s['quality_reasons']} fi={s['fi']:.1f} fi_valid={s['fi_valid']} fi_provisional={s['fi_provisional']} control_state={s['control_state']}")
        time.sleep(0.1)
    return 0

if __name__=='__main__':
    raise SystemExit(main())
