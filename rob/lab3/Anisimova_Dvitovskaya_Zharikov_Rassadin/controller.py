from vehicle import Driver

# Блок начальной инициализации. Вдруг кто не знает.

# name of the available distance sensors
sensorsNames = [
    'front',
    'front right 0',
    'front right 1',
    'front right 2',
    'front left 0',
    'front left 1',
    'front left 2',
    'rear',
    'rear left',
    'rear right',
    'right',
    'left']
sensors = {}

#выставим максимальную скорость, загрузка водителя и установка угла поворота колес в 0.0
maxSpeed = 50
driver = Driver()
driver.setSteeringAngle(0.0)

# get and enable the distance sensors
for name in sensorsNames:
    sensors[name] = driver.getDistanceSensor('distance sensor ' + name)
    sensors[name].enable(10)

#define values for PID
kp = 0.12        # коэффициент пропорциональной составляющей
ki = 0.0022      # коэффициент интегральной составляющей
kd = 1           # коэффициент дифференциальной составляющей

iMin = -1.0      # минимальная сумма ошибок интегральной составляющей
iMax = 1.0       # максимальная сумма ошибок интегральной составляющей

iSum = 0.0       # сумма ошибок интегральной составляющей. Изначально равна 0.

oldY = 0.0       # Отклонение на предыдущей итерации. Изначально примем равным 0.

# бесконечный цикл работы контроллера. Мало ли, вдруг кто не знает.
while driver.step() != -1:
    
    ################# БЛОК РЕГУЛИРОВКИ СКОРОСТИ ####################
    
    # настройка круизной скорости в зависимости от расстояния до
    # объекта впереди.
    frontDistance = sensors['front'].getValue()
    frontRange = sensors['front'].getMaxValue()
    speed = maxSpeed * frontDistance / frontRange
    driver.setCruisingSpeed(speed)
    # нажать на тормоз чтобы снизить скорость. Сила нажатия 
    # определяется тем, как сильно отличаются реальная и 
    # желаемая скорости, но не больше 1 (100%).
    speedDiff = driver.getCurrentSpeed() - speed
    if speedDiff > 0:
        driver.setBrakeIntensity(min(speedDiff / speed, 1))
    # если реальная скорость ниже желаемой, отпустить педаль тормоза
    else:
        driver.setBrakeIntensity(0)
    
    ################## БЛОК PID-РЕГУЛЯТОРА #######################
    
    # полученние данных с правого датчика.
    rightDistance = sensors['right'].getValue()
    # 6.0 - примерно середина полосы, rightDiff - отклонение от середины полосы.
    rightDiff = rightDistance - 6.0
    # up - пропорциональная составляющая, kp - коэффициент пропорциональной составляющей
    up=kp*rightDiff
    
    #Вычисляем интегральную составляющую.
    #iSum - сумма накопленных ошибок. Ошибка берется с минусом, 
    #потому что нам нужно исправлять её, а не увеличивать
    iSum-=rightDiff
    # Ограничим максимальную и минимальную сумму ошибок
    #Иначе раскачает
    if (iSum > iMax) : iSum=iMax
    else:
        if (iSum < iMin): iSum=iMin
    #ui - интегральная составляющая. ki - коэффициент интегральной составляющей
    ui= ki*iSum
    
    #ud - дифференциальная составляющая. kd - коэффициент дифференциальной составляющей
    #В дифференциальной составляющей определяется насколько мы продолжаем отклоняться от курса
    #независимо от работы пропорциональной составляющей. Если пропорциональной не хватает
    #дифференциальная добавит угол, Если пропорциональная будет излишне поворачивать, 
    #дифференциальная замедлит. разница между предыдущим отклонением от середины полосы
    #и текущим умножается на коэффициент kd.
    ud = kd* (rightDiff-oldY)
    
    #Вычисляем итоговый угол поворота как сумму всех 3 составляющих.
    sumAngle = up+ui+ud
    
    #Назначаем полученный угол
    driver.setSteeringAngle(sumAngle)
    
    #Запоминаем текущее значение отклонения от линии для следующей итерации.
    oldY = rightDiff
