"""
\brief Tests for LinearTopology

\author Yasuyuki Tanaka <yasuyuki.tanaka@inria.fr>
"""

import SimEngine.Mote as Mote


def test_linear_topology_with_3_motes(motes):

    motes = motes(3)
    assert len(motes) == 3
    assert motes[0].x == 0 and motes[0].y == 0
    assert motes[1].x == 0.03 and motes[0].y == 0
    assert motes[2].x == 0.06 and motes[0].y == 0
    assert motes[0].PDR == {motes[1]: 1.0}
    assert motes[1].PDR == {motes[0]: 1.0, motes[2]: 1.0}
    assert motes[2].PDR == {motes[1]: 1.0}
    assert motes[1].id in motes[0].RSSI
    assert motes[2].id in motes[0].RSSI
    assert motes[0].id in motes[1].RSSI
    assert motes[2].id in motes[1].RSSI
    assert motes[0].id in motes[2].RSSI
    assert motes[1].id in motes[2].RSSI


def test_linear_topology_4_motes(motes):

    motes = motes(4)
    assert len(motes) == 4
    assert motes[0].x == 0 and motes[0].y == 0
    assert motes[1].x == 0.03 and motes[0].y == 0
    assert motes[2].x == 0.06 and motes[0].y == 0
    assert motes[3].x == 0.09 and motes[0].y == 0
    assert motes[0].PDR == {motes[1]: 1.0}
    assert motes[2].PDR == {motes[1]: 1.0, motes[3]: 1.0}
    assert motes[3].PDR == {motes[2]: 1.0}
    assert motes[1].id in motes[0].RSSI
    assert motes[2].id in motes[0].RSSI
    assert motes[3].id in motes[0].RSSI
    assert motes[0].id in motes[1].RSSI
    assert motes[2].id in motes[1].RSSI
    assert motes[3].id in motes[1].RSSI
    assert motes[0].id in motes[2].RSSI
    assert motes[1].id in motes[2].RSSI
    assert motes[3].id in motes[2].RSSI
    assert motes[0].id in motes[3].RSSI
    assert motes[1].id in motes[3].RSSI
    assert motes[2].id in motes[3].RSSI


def test_rpl_tree_builder(motes):

    motes = motes(4, **{'withJoin': False})

    assert motes[0].dagRoot is True
    assert motes[0].preferredParent is None
    assert motes[0].parents[(1,)] == [[0]]
    assert motes[0].parents[(2,)] == [[1]]
    assert motes[0].parents[(3,)] == [[2]]
    assert motes[0].rank == Mote.RPL_MIN_HOP_RANK_INCREASE
    assert motes[0].dagRank == 1

    assert motes[1].dagRoot is False
    assert motes[1].preferredParent == motes[0]
    assert motes[1].rank == Mote.RPL_MIN_HOP_RANK_INCREASE * 8
    assert motes[1].dagRank == 8

    assert motes[2].dagRoot is False
    assert motes[2].preferredParent == motes[1]
    assert motes[2].rank == Mote.RPL_MIN_HOP_RANK_INCREASE * 15
    assert motes[2].dagRank == 15

    assert motes[3].dagRoot is False
    assert motes[3].preferredParent == motes[2]
    assert motes[3].rank == Mote.RPL_MIN_HOP_RANK_INCREASE * 22
    assert motes[3].dagRank == 22


def test_linear_schedule_installation_1(motes):

    motes = motes(3, **{'withJoin': False})

    assert motes[0].numCellsToNeighbors == {}
    assert motes[0].numCellsFromNeighbors[motes[1]] == 1
    assert len(motes[0].schedule) == 2
    assert motes[0].schedule[0]['ch'] == 0
    assert motes[0].schedule[0]['dir'] == Mote.DIR_TXRX_SHARED
    assert motes[0].schedule[0]['neighbor'] == [motes[1]]
    assert motes[0].schedule[2]['ch'] == 0
    assert motes[0].schedule[2]['dir'] == Mote.DIR_RX
    assert motes[0].schedule[2]['neighbor'] == motes[1]

    assert motes[1].numCellsToNeighbors[motes[0]] == 1
    assert motes[1].numCellsFromNeighbors[motes[2]] == 1
    assert len(motes[1].schedule) == 3
    assert motes[1].schedule[0]['ch'] == 0
    assert motes[1].schedule[0]['dir'] == Mote.DIR_TXRX_SHARED
    assert len(motes[1].schedule[0]['neighbor']) == 2
    assert motes[0] in motes[1].schedule[0]['neighbor']
    assert motes[2] in motes[1].schedule[0]['neighbor']
    assert motes[1].schedule[1]['ch'] == 0
    assert motes[1].schedule[1]['dir'] == Mote.DIR_RX
    assert motes[1].schedule[1]['neighbor'] == motes[2]
    assert motes[1].schedule[2]['ch'] == 0
    assert motes[1].schedule[2]['dir'] == Mote.DIR_TX
    assert motes[1].schedule[2]['neighbor'] == motes[0]

    assert motes[2].numCellsToNeighbors[motes[1]] == 1
    assert motes[2].numCellsFromNeighbors == {}
    assert len(motes[2].schedule) == 2
    assert motes[2].schedule[0]['ch'] == 0
    assert motes[2].schedule[0]['dir'] == Mote.DIR_TXRX_SHARED
    assert motes[2].schedule[0]['neighbor'] == [motes[1]]
    assert motes[2].schedule[1]['ch'] == 0
    assert motes[2].schedule[1]['dir'] == Mote.DIR_TX
    assert motes[2].schedule[1]['neighbor'] == motes[1]


def test_linear_schedule_installation_2(motes):

    motes = motes(8, **{'withJoin': False})

    assert motes[7].schedule[1]['ch'] == 0
    assert motes[7].schedule[1]['dir'] == Mote.DIR_TX
    assert motes[7].schedule[1]['neighbor'] == motes[6]

    assert motes[6].schedule[1]['ch'] == 0
    assert motes[6].schedule[1]['dir'] == Mote.DIR_RX
    assert motes[6].schedule[1]['neighbor'] == motes[7]
    assert motes[6].schedule[2]['ch'] == 0
    assert motes[6].schedule[2]['dir'] == Mote.DIR_TX
    assert motes[6].schedule[2]['neighbor'] == motes[5]

    assert motes[5].schedule[2]['ch'] == 0
    assert motes[5].schedule[2]['dir'] == Mote.DIR_RX
    assert motes[5].schedule[2]['neighbor'] == motes[6]
    assert motes[5].schedule[3]['ch'] == 0
    assert motes[5].schedule[3]['dir'] == Mote.DIR_TX
    assert motes[5].schedule[3]['neighbor'] == motes[4]

    assert motes[4].schedule[3]['ch'] == 0
    assert motes[4].schedule[3]['dir'] == Mote.DIR_RX
    assert motes[4].schedule[3]['neighbor'] == motes[5]
    assert motes[4].schedule[4]['ch'] == 0
    assert motes[4].schedule[4]['dir'] == Mote.DIR_TX
    assert motes[4].schedule[4]['neighbor'] == motes[3]

    assert motes[3].schedule[4]['ch'] == 0
    assert motes[3].schedule[4]['dir'] == Mote.DIR_RX
    assert motes[3].schedule[4]['neighbor'] == motes[4]
    assert motes[3].schedule[5]['ch'] == 0
    assert motes[3].schedule[5]['dir'] == Mote.DIR_TX
    assert motes[3].schedule[5]['neighbor'] == motes[2]

    assert motes[2].schedule[5]['ch'] == 0
    assert motes[2].schedule[5]['dir'] == Mote.DIR_RX
    assert motes[2].schedule[5]['neighbor'] == motes[3]
    assert motes[2].schedule[6]['ch'] == 0
    assert motes[2].schedule[6]['dir'] == Mote.DIR_TX
    assert motes[2].schedule[6]['neighbor'] == motes[1]

    assert motes[1].schedule[6]['ch'] == 0
    assert motes[1].schedule[6]['dir'] == Mote.DIR_RX
    assert motes[1].schedule[6]['neighbor'] == motes[2]
    assert motes[1].schedule[7]['ch'] == 0
    assert motes[1].schedule[7]['dir'] == Mote.DIR_TX
    assert motes[1].schedule[7]['neighbor'] == motes[0]

    assert motes[0].schedule[7]['ch'] == 0
    assert motes[0].schedule[7]['dir'] == Mote.DIR_RX
    assert motes[0].schedule[7]['neighbor'] == motes[1]
