import argparse,time
from relic_core.bridge_adapter import MockDataBridge,LiveDataBridgeAdapter
from relic_core.runtime import AppCore

def main():
    p=argparse.ArgumentParser(); p.add_argument('--mock',action='store_true'); p.add_argument('--bridge',choices=['live','mock'],default='mock'); p.add_argument('--host',default='127.0.0.1'); p.add_argument('--port',type=int,default=8000); p.add_argument('--ticks',type=int,default=20); p.add_argument('--interval',type=float,default=0.5); p.add_argument('--debug',action='store_true'); p.add_argument('--game',default='empty_game'); a=p.parse_args()
    mode='mock' if a.mock else a.bridge
    bridge=MockDataBridge() if mode=='mock' else LiveDataBridgeAdapter(host=a.host,port=a.port)
    try:
        core=AppCore(bridge); core.start(); core.start_game(a.game)
    except Exception as e:
        print(f'[RELIC CORE] live bridge start failed: {e}. 建议使用 --mock 测试核心。'); return
    print(f'[RELIC CORE] bridge={mode} session={core.session_manager.info.session_id}')
    try:
        for i in range(1,a.ticks+1):
            out=core.tick(int(a.interval*1000)); s=out['snapshot']; q=out['quality']; f=out['focus']
            print(f"tick={i} connected={out['bridge_connected']} bridge_alive={out['bridge_alive']} stream={out['stream_state']} sensor_stream_active={out['sensor_stream_active']} training_data_valid={out['training_data_valid']} attention={s.get('attention_value')} attention_age_ms={s.get('attention_age_ms')} last_algorithm_age_ms={s.get('last_algorithm_msg_age_ms')} focus=({s.get('focus_x')},{s.get('focus_y')}) gyro=({s.get('gyro_x')},{s.get('gyro_y')},{s.get('gyro_z')}) gyro_age_ms={s.get('gyro_age_ms')} sqi={q.get('sqi'):.2f} quality={q.get('status')} reasons={q.get('reasons')} fi={f.get('fi'):.1f} state={out['focus_state']} game={out['current_game']}")
            time.sleep(a.interval)
    except KeyboardInterrupt:
        print('Interrupted, cleaning up...')
    finally:
        core.end_game('stop'); core.cleanup()
if __name__=='__main__': main()
