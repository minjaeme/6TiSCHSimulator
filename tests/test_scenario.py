import pytest

import test_utils as u

# =========================== fixtures ========================================

@pytest.fixture(params=[2])
def fixture_exec_numMotes(request):
    return request.param

#@pytest.fixture(params=['up', 'down', 'up-down'])
@pytest.fixture(params=['up'])
def fixture_data_flow(request):
    return request.param

#@pytest.fixture(params=[10, 100, 200])
@pytest.fixture(params=[10])
def fixture_app_pkLength(request):
    return request.param

#@pytest.fixture(params=["PerHopReassembly", "FragmentForwarding"])
@pytest.fixture(params=["FragmentForwarding"])
def fixture_fragmentation(request):
    return request.param

#@pytest.fixture(params=[True, False])
@pytest.fixture(params=[False])
def fixture_ff_vrb_policy_missing_fragment(request):
    return request.param

#@pytest.fixture(params=[True, False])
@pytest.fixture(params=[False])
def fixture_ff_vrb_policy_last_fragment(request):
    return request.param

@pytest.fixture(params=['SSFSymmetric'])
def fixture_sf_type(request):
    return request.param

# =========================== helpers =========================================

def check_all_nodes_send_x(motes,x):
    senders = list(set([l['mote_id'] for l in u.read_log_file(['tsch.txdone']) if l['frame_type']==x]))
    assert sorted(senders)==sorted([m.id for m in motes])

# === RPL

def rpl_check_root_parentChildfromDAOs(motes):
    root = motes[0]
    
    # assuming a linear topology
    expected = {}
    for m in motes:
        if m.id==0:
            continue
        expected[m.id] = m.id-1
    
    assert root.rpl.parentChildfromDAOs == expected

def rpl_check_all_node_prefered_parent(motes):
    """ Verify that each mote has a prefered parent """
    for mote in motes:
        if mote.dagRoot:
            continue
        else:
            assert mote.rpl.getPreferredParent() is not None

def rpl_check_all_node_rank(motes):
    """ Verify that each mote has a rank """
    for mote in motes:
        assert mote.rpl.getRank() is not None

def rpl_check_all_nodes_send_DIOs(motes):
    check_all_nodes_send_x(motes,'DIO')

def rpl_check_all_motes_send_DAOs(motes):
    senders = list(set([l['mote_id'] for l in u.read_log_file(['tsch.txdone']) if l['frame_type']=='DAO']))
    assert sorted(senders)==sorted([m.id for m in motes if m.id!=0])

# === TSCH

def tsch_all_nodes_check_dedicated_cell(motes):
    """ Verify that each mote has at least:
            - one TX cell to its preferred parent
            - one RX cell per child
    """
    for mote in motes:
        parent = mote.rpl.getPreferredParent()

        # at least one TX cell to its preferred parent
        tx_cell_exists = False
        for cell in mote.tsch.getTxCells():
            for neighbor in cell['neighbor']:
                if neighbor == parent:
                    tx_cell_exists = True
                    break
        assert tx_cell_exists

def tsch_check_all_nodes_send_EBs(motes):
    check_all_nodes_send_x(motes,'EB')

def tsch_check_all_nodes_synced(motes):
    synced =  list(set([l['mote_id'] for l in u.read_log_file(['tsch.synced'])]))
    assert sorted(synced)==sorted([m.id for m in motes])

# =========================== tests ===========================================

def test_vanilla_scenario(
        sim_engine,
        fixture_exec_numMotes,
        fixture_data_flow,
        fixture_app_pkLength,
        fixture_fragmentation,
        fixture_ff_vrb_policy_missing_fragment,
        fixture_ff_vrb_policy_last_fragment,
        fixture_sf_type,
    ):
    """
    Let the network form, send data packets up and down.
    """

    # initialize the simulator
    fragmentation_ff_discard_vrb_entry_policy = []
    if fixture_ff_vrb_policy_missing_fragment:
        fragmentation_ff_discard_vrb_entry_policy += ['missing_fragment']
    if fixture_ff_vrb_policy_last_fragment:
        fragmentation_ff_discard_vrb_entry_policy += ['last_fragment']
    sim_engine = sim_engine(
        diff_config = {
            'exec_numMotes':                               fixture_exec_numMotes,
            'exec_numSlotframesPerRun':                    10000,
            'app_pkLength' :                               fixture_app_pkLength,
            'app_pkPeriod':                                0, # disable, will be send by test
            'rpl_daoPeriod':                               30,
            "tsch_probBcast_ebProb":                       0.10,
            "tsch_probBcast_dioProb":                      0.10,
            'fragmentation':                               fixture_fragmentation,
            'fragmentation_ff_discard_vrb_entry_policy':   fragmentation_ff_discard_vrb_entry_policy,
            'sf_type':                                     fixture_sf_type,
            'conn_type':                                   'linear',
        },
    )
    
    # === network forms
    
    # give the network time to form
    u.run_until_asn(sim_engine, 300*100)
    
    # verify that all nodes are sync'ed
    tsch_check_all_nodes_synced(sim_engine.motes)
    
    # verify that all nodes are sending EBs, DIOs and DAOs
    tsch_check_all_nodes_send_EBs(sim_engine.motes)
    rpl_check_all_nodes_send_DIOs(sim_engine.motes)
    rpl_check_all_motes_send_DAOs(sim_engine.motes)
    
    # verify that all nodes have acquired rank and preferred parent
    rpl_check_all_node_prefered_parent(sim_engine.motes)
    rpl_check_all_node_rank(sim_engine.motes)
    
    # verify that root has stored enough DAO information to compute source routes
    rpl_check_root_parentChildfromDAOs(sim_engine.motes)
    
    # verify that all nodes have a dedicated cell to their parent
    if fixture_sf_type!='SSFSymmetric':
        tsch_all_nodes_check_dedicated_cell(sim_engine.motes)
    
    # === send data up/down
    
    # pick a "datamote" which will send/receive data
    datamote = sim_engine.motes[-1] # pick furthest mote

    # get the DAG root
    dagroot  = sim_engine.motes[sim_engine.DAGROOT_ID]
    
    # verify no packets yet received by root
    assert len(u.read_log_file(['app.rx']))==0
    
    # send data upstream (datamote->root)
    if fixture_data_flow.find("up")!=-1:
        
        # inject data at the datamote
        datamote.app._action_mote_sendSinglePacketToDAGroot()

        # give the data time to reach the root
        u.run_until_asn(sim_engine, sim_engine.getAsn() + 10000)

        # verify it got to the root
        assert len(u.read_log_file(['app.rx']))>0
    
    # send data downstream (root->datamote)
    if fixture_data_flow.find("down")!=-1:
        
        # inject data at the root
        dagroot.app._action_root_sendSinglePacketToMote(datamote)

        # give the data time to reach the datamote
        u.run_until_asn(sim_engine, sim_engine.getAsn() + 10000)

        # verify it got to the root
        #assert len(u.read_log_file(['app_reaches_mote']))>0
