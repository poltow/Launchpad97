try:
    from _Framework.Capabilities import CONTROLLER_ID_KEY, PORTS_KEY, NOTES_CC, SCRIPT, SYNC, REMOTE, controller_id, inport, outport
    try:
        from .LaunchpadLooper import LaunchpadLooper
    except (ImportError, ValueError):
        from LaunchpadLooper import LaunchpadLooper
    _IN_LIVE = True
except ImportError:
    _IN_LIVE = False


def create_instance(c_instance):
    return LaunchpadLooper(c_instance)


def get_capabilities():
    return {
        CONTROLLER_ID_KEY: controller_id(
            vendor_id=4661,
            product_ids=[14, 32, 54],
            model_name=['Launchpad', 'Launchpad S', 'Launchpad Mini']),
        PORTS_KEY: [
            inport(props=[NOTES_CC, SCRIPT, REMOTE]),
            outport(props=[NOTES_CC, SCRIPT, SYNC, REMOTE])]
    }
