from onl.sim import Environment
from onl.netdev import Wire
from sender import GBNSender
from receiver import GBNReceiver

seqno_width = 4
window_size = 15
loss_rate = 0.1
timeout = 30.0 
message = """
Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula
eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient
montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque
eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo,
fringilla vel, aliquet nec, vulputate eget, arcu. In enim justo, rhoncus ut,
imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium.
Integer tincidunt. Cras dapibus. Vivamus elementum semper nisi. Aenean vulputate
eleifend tellus. Aenean leo ligula, porttitor eu, consequat vitae, eleifend ac,
enim. Aliquam lorem ante, dapibus in, viverra quis, feugiat a, tellus. Phasellus
viverra nulla ut metus varius laoreet. Quisque rutrum. Aenean imperdiet. Etiam
ultricies nisi vel augue. Curabitur ullamcorper ultricies nisi. Nam eget dui.
Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper
libero, sit amet adipiscing sem neque sed ipsum. Nam quam nunc, blandit vel,
luctus pulvinar, hendrerit id, lorem. Maecenas nec odio et ante tincidunt
tempus. Donec vitae sapien ut libero venenatis faucibus. Nullam quis ante. Etiam
sit amet orci eget eros faucibus tincidunt. Duis leo. Sed fringilla mauris sit
amet nibh. Donec sodales sagittis magna. Sed consequat, leo eget bibendum
sodales, augue velit cursus nunc,
"""
env = Environment()
sender = GBNSender(
    env,
    seqno_width=seqno_width,
    timeout=timeout,
    window_size=window_size,
    message=message,
    debug=True,
)
receiver = GBNReceiver(
    env,
    seqno_width=seqno_width,
    window_size=window_size,
    debug=True
)
wire1 = Wire(env, delay_dist=lambda: 10, loss_rate=0.1, debug=False)
wire2 = Wire(env, delay_dist=lambda: 10)
sender.out = wire1
wire1.out = receiver
receiver.out = wire2
wire2.out = sender

env.run(sender.proc)

assert receiver.message == message
