from wiliot.wiliot_testers.offline.offline_utils import *
from time import sleep

class tadbikR2rController():
    def __init__(self):
        self.my_gpio = R2rGpio()
        self.GwObj = WiliotGateway(auto_connect=True, logger_name='root')
        self.GwObj.reset_gw()


    def stop(self):
        self.my_gpio.gpio_state(3, "OFF")

    def start(self):
        self.my_gpio.gpio_state(3, "ON")

    def failed(self):
        self.my_gpio.pulse(2, 50)

    def passed(self):
        self.my_gpio.pulse(1, 50)

    def set_missing_label_state(self,state = "ON"):
        self.my_gpio.gpio_state(4, state)

    def toggle_direction(self):
        self.my_gpio.pulse(5, 50)

    def restart(self):
        self.stop()
        self.start()

    def is_r2r_moved(self):
        gw_answer = self.GwObj.read_specific_message(msg="Start Production Line GW", read_timeout=1,
                                         clear=False)
        if gw_answer == '':
            return False
        else:
            return True

    def rewind(self, max_missing_labels=6, num_tags=0):
        assert max_missing_labels>0, f"max missing labels must be bigger than zero, got {max_missing_labels}"
        done = False
        missing_label_counter = 0
        self.GwObj.start_continuous_listener()
        self.restart()
        self.toggle_direction()
        tags_counter = 0
        missing_labels_stop = False
        while not done:
            self.passed()
            if not self.is_r2r_moved():
                missing_label_counter += 1
                print(f"missing labels {missing_label_counter}")
                if missing_label_counter >= max_missing_labels:
                    print(f"Rewind finished after {missing_label_counter} missing labels")
                    missing_labels_stop = True
                    done = True
                else:
                    self.restart()
                    self.toggle_direction()
            else:
                tags_counter += 1
                if num_tags != 0 and tags_counter >= num_tags:
                    done = True
                    print(f"Rewind finished after {tags_counter} tags")

        if missing_labels_stop:
            print("start searching for first tag")
            missing_label_counter = 0
            while not self.is_r2r_moved():
                self.restart()
                self.passed()
                missing_label_counter += 1
                print(f"missing labels {missing_label_counter}")
                if missing_label_counter > 100:
                    print("Start of reel wasn't found for 100 tags!")
                    break;

            print("Roll to first tag:")
            locations_from_sensor_to_dut = 8
            for num_tags in range(locations_from_sensor_to_dut):
                self.restart()
                self.passed()
        self.GwObj.stop_continuous_listener()
        self.stop()

            

if __name__ == '__main__':
    tadbik_r2r_controller = tadbikR2rController()
    tadbik_r2r_controller.rewind(max_missing_labels=6)
    print("Done!")




