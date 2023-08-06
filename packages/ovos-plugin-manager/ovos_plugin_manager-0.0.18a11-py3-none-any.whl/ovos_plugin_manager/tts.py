from ovos_plugin_manager.utils import load_plugin, find_plugins, PluginTypes
from ovos_plugin_manager.templates.tts import TTS
from ovos_config import Configuration
from ovos_utils.log import LOG


def find_tts_plugins():
    return find_plugins(PluginTypes.TTS)


def load_tts_plugin(module_name):
    """Wrapper function for loading tts plugin.

    Arguments:
        (str) Mycroft tts module name from config
    Returns:
        class: found tts plugin class
    """
    return load_plugin(module_name, PluginTypes.TTS)


class OVOSTTSFactory:
    """ replicates the base mycroft class, but uses only OPM enabled plugins"""
    MAPPINGS = {
        "dummy": "ovos-tts-plugin-dummy",
        "mimic": "ovos-tts-plugin-mimic",
        "mimic2": "ovos-tts-plugin-mimic2",
        "mimic3": "ovos-tts-plugin-mimic3",
        "google": "ovos-tts-plugin-google-tx",
        "marytts": "ovos-tts-plugin-marytts",
        # "fatts": FATTS,
        # "festival": Festival,
        "espeak": "ovos_tts_plugin_espeakng",
        # "spdsay": SpdSay,
        # "watson": WatsonTTS,
        # "bing": BingTTS,
        "responsive_voice": "ovos-tts-plugin-responsivevoice",
        # "yandex": YandexTTS,
        "polly": "ovos-tts-plugin-polly",
        # "mozilla": MozillaTTS,
        "pico": "ovos-tts-plugin-pico"
    }

    @staticmethod
    def get_class(config=None):
        """Factory method to get a TTS engine class based on configuration.

        The configuration file ``mycroft.conf`` contains a ``tts`` section with
        the name of a TTS module to be read by this method.

        "tts": {
            "module": <engine_name>
        }
        """
        config = config or get_tts_config()
        tts_module = config.get("module") or "dummy"
        if tts_module in OVOSTTSFactory.MAPPINGS:
            tts_module = OVOSTTSFactory.MAPPINGS[tts_module]
        return load_tts_plugin(tts_module)

    @staticmethod
    def create(config=None):
        """Factory method to create a TTS engine based on configuration.

        The configuration file ``mycroft.conf`` contains a ``tts`` section with
        the name of a TTS module to be read by this method.

        "tts": {
            "module": <engine_name>
        }
        """
        tts_config = get_tts_config(config)
        tts_lang = tts_config["lang"]
        tts_module = tts_config.get('module', 'dummy')
        try:
            clazz = OVOSTTSFactory.get_class(tts_config)
            if clazz:
                LOG.info(f'Found plugin {tts_module}')
                tts = clazz(tts_lang, tts_config)
                tts.validator.validate()
                LOG.info(f'Loaded plugin {tts_module}')
            else:
                raise FileNotFoundError("unknown plugin")
        except Exception:
            LOG.exception('The selected TTS plugin could not be loaded.')
            raise
        return tts


def get_tts_config(config=None):
    config = config or Configuration()
    lang = config.get("lang", "en-us")
    if "tts" in config and "module" in config["tts"]:
        config = config["tts"]
    tts_module = config.get('module') or "dummy"
    tts_config = config.get(tts_module, {})
    tts_config["lang"] = tts_config.get('lang') or lang
    tts_config["module"] = tts_module
    return tts_config
