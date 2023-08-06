from datetime import datetime
from .dates import localize
from .init_creds import init_mongo
from .dates import today_argentina

db = init_mongo()


def member_unsubscribe(member: dict, reason, source, unsubscribe_request=False, status_boleta_inactivado='expired'):
    """ Da de baja un socio modificando los parámetros necesarios
       :param member: objeto de cliente a dar de baja
       :type receiver: dict
       :param reason: motivo de la baja
       :type template: str
       :param unsubscribe_request: es True si el cliente es 'baja' y puede seguir ingresando
       :type unsubscribe_request: bool, optional
       :return: None
       :rtype: None
       """
    
    status = 'baja' if unsubscribe_request else 'inactivo'

    history_event = create_history_event(member, status, source, reason)

    db.clientes.update_one(
        {"_id": member["_id"]},
        {
            "$push": {
                "history2": history_event
            },
            "$set": {
                "next_payment_date": None,
                "status": status
            }
        }
    )

    db.boletas.update_many(
        {
            "member_id": member["_id"],
            "status": {
                "$in": ["error", "rejected"]
            }
        },
        {
            "$set": {
                "status": status_boleta_inactivado
            }
        }
    )


def create_history_event(member, event_type, source, reason=None):

    history_event = {
        'event': event_type,
        'date_created': today_argentina(),
        'source': source
    }
    if reason:
        history_event["reason"] = reason

    if event_type in ['alta', 'baja', 'inactivacion', 'revertir_baja']:
        history_event['plan'] = member["active_plan_id"]
    
        if 'discounts' in member and member["discounts"] and len(member["discounts"]) > 0:
            history_event['discounts'] = member['discounts']
    
    elif event_type == "cambio_tarjeta":
        history_event["card_id"] = member["active_card"]

    return history_event