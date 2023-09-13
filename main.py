import struct
import my_serial as messager
from game_set import Scene
from threading import Thread


def find_0xa5(_ser):
    global scene
    last_bytes = 0
    while not scene.exit_signal:
        current_bytes = _ser.in_waiting
        if last_bytes - current_bytes < -30:
            length = 30
            _info = _ser.read(length)

            for _index, number in enumerate(_info):
                if number == 165:
                    if _index + 4 < length:
                        print('ok', _index, length)
                        _data_length = _info[_index + 1] + _info[_index + 2] * 256
                        seq = _info[_index + 3]
                        CRC8 = _info[_index + 4]

                        _header = messager.struct.pack('B', 165) + \
                                  messager.struct.pack('H', _data_length) + \
                                  messager.struct.pack('B', seq)

                        crc8 = messager.get_crc8_check_byte(_header)
                        if CRC8 == crc8:
                            print('success!')
                            return _index, _info[_index:]
            last_bytes = current_bytes


def serial_receive(_ser):
    global scene

    index, info = find_0xa5(_ser)
    data_length = info[1] + info[2] * 256

    # 保证 read 同步至一个帧尾
    while not scene.exit_signal:
        if data_length + 9 - len(info) > 0:  # 未读完当前段
            _ser.read(data_length + 9 - len(info))
            break
        else:  # 当前段全部位于info中
            info = info[data_length + 9:]
            if len(info) >= 3:
                data_length = info[1] + info[2] * 256
            else:
                _ser.read()

    while not scene.exit_signal:
        header = messager.recv(_ser, 5)

        if len(header) == 5:
            data_length = header[0] + header[1] * 256
            frame_length = 2 + data_length + 2
            frame_body = _ser.read(frame_length)
            if frame_length > 4:
                cmd_id = frame_body[0] + frame_body[1] * 256
                # 0503
                if cmd_id == 773:
                    num_in_bytes = frame_body[2:4]
                    x_in_bytes = frame_body[4:8]
                    y_in_bytes = frame_body[8:12]

                    num = struct.unpack('h', num_in_bytes)
                    x = struct.unpack('f', x_in_bytes)
                    y = struct.unpack('f', y_in_bytes)
                    # print(int(num[0] - 101))

                    x = int(x[0] * 1412 / 28000 * 1000)
                    y = 757 - int(y[0] * 757 / 15000 * 1000)
                    print(str(num[0]) + ' x: ' + str(x) + ' y: ' + str(y))
                    if 1 <= num[0] <= 5:
                        scene.red_cars.sprites()[int(num[0] - 1)].move_to(x, y)
                    elif 101 <= num[0] <= 105:
                        scene.blue_cars.sprites()[int(num[0] - 101)].move_to(x, y)
                # 0201/0202/0203
        else:
            # 保证 read 同步至一个帧尾
            while not scene.exit_signal:
                if data_length + 9 - len(info) > 0:  # 未读完当前段
                    _ser.read(data_length + 9 - len(info))
                    break
                else:  # 当前段全部位于info中
                    info = info[data_length + 9:]
                    if len(info) >= 3:
                        data_length = info[1] + info[2] * 256
                    else:
                        _ser.read()

    print('Serial Receive Thread Exit!')


portx = 'COM8'
ser = messager.serial_init(portx)
msg_thread = Thread(target=serial_receive, kwargs={'ser': ser}, name='Serial_Read_Thread')
scene = Scene(1412, 757, msg_thread)  # Scene(1200, 600)

if __name__ == '__main__':
    scene.run()
