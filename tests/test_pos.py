from mpqr.pos_client import POSClient

def test_create_and_get_pos():
    cli = POSClient()
    pos = cli.create_pos("PB_CAJA1", "Caja PB")
    assert pos["name"] == "Caja PB"

    pos2 = cli.get_pos("PB_CAJA1")
    assert pos2["external_id"] == "PB_CAJA1"
