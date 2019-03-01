from enum import Enum


class VPNConfigurationPlatform(Enum):
    __version__ = 1

    def __new__(cls, *args, **kwds):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, sid, text):
        self.sid = sid
        self.text = text

    @staticmethod
    def find_by_text(text):
        if VPNConfigurationPlatform.IOS.text == text:
            return VPNConfigurationPlatform.IOS
        elif VPNConfigurationPlatform.ANDROID.text == text:
            return VPNConfigurationPlatform.ANDROID
        elif VPNConfigurationPlatform.WINDOWS.text == text:
            return VPNConfigurationPlatform.WINDOWS
        elif VPNConfigurationPlatform.MACOS.text == text:
            return VPNConfigurationPlatform.MACOS

    @staticmethod
    def find_by_sid(sid):
        if VPNConfigurationPlatform.IOS.sid == sid:
            return VPNConfigurationPlatform.IOS
        elif VPNConfigurationPlatform.ANDROID.sid == sid:
            return VPNConfigurationPlatform.ANDROID
        elif VPNConfigurationPlatform.WINDOWS.sid == sid:
            return VPNConfigurationPlatform.WINDOWS
        elif VPNConfigurationPlatform.MACOS.sid == sid:
            return VPNConfigurationPlatform.MACOS

    IOS = (1, 'ios')
    ANDROID = (2, 'android')
    WINDOWS = (3, 'windows')
    MACOS = (4, 'macos')
