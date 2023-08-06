import warnings
import numpy as np
import sys
import math
import os
import pickle
from statistics import mode

warnings.filterwarnings('ignore')
PCPNS = ['H1', 'H2', 'NCI', 'P1', 'P2', 'SASA', 'V']
AAPCPVS = {
'A': {'H1': 0.62, 'H2': -0.5, 'NCI': 0.007187, 'P1': 8.1, 'P2': 0.046, 'SASA': 1.181, 'V': 27.5},
'C': {'H1': 0.29, 'H2': -1.0, 'NCI': -0.036610, 'P1': 5.5, 'P2': 0.128, 'SASA': 1.461, 'V': 44.6},
'D': {'H1': -0.90, 'H2': 3.0, 'NCI': -0.023820, 'P1': 13.0, 'P2': 0.105, 'SASA': 1.587, 'V': 40.0},
'E': {'H1': 0.74, 'H2': 3.0, 'NCI': 0.006802, 'P1': 12.3, 'P2': 0.151, 'SASA': 1.862, 'V': 62.0},
'F': {'H1': 1.19, 'H2': -2.5, 'NCI': 0.037552, 'P1': 5.2, 'P2': 0.290, 'SASA': 2.228, 'V': 115.5},
'G': {'H1': 0.48, 'H2': 0.0, 'NCI': 0.179052, 'P1': 9.0, 'P2': 0.000, 'SASA': 0.881, 'V': 0.0},
'H': {'H1': -0.40, 'H2': -0.5, 'NCI': -0.010690, 'P1': 10.4, 'P2': 0.230, 'SASA': 2.025, 'V': 79.0},
'I': {'H1': 1.38, 'H2': -1.8, 'NCI': 0.021631, 'P1': 5.2, 'P2': 0.186, 'SASA': 1.810, 'V': 93.5},
'K': {'H1': -1.50, 'H2': 3.0, 'NCI': 0.017708, 'P1': 11.3, 'P2': 0.219, 'SASA': 2.258, 'V': 100.0},
'L': {'H1': 1.06, 'H2': -1.8, 'NCI': 0.051672, 'P1': 4.9, 'P2': 0.186, 'SASA': 1.931, 'V': 93.5},
'M': {'H1': 0.64, 'H2': -1.3, 'NCI': 0.002683, 'P1': 5.7, 'P2': 0.221, 'SASA': 2.034, 'V': 94.1},
'N': {'H1': -0.78, 'H2': 2.0, 'NCI': 0.005392, 'P1': 11.6, 'P2': 0.134, 'SASA': 1.655, 'V': 58.7},
'P': {'H1': 0.12, 'H2': 0.0, 'NCI': 0.239531, 'P1': 8.0, 'P2': 0.131, 'SASA': 1.468, 'V': 41.9},
'Q': {'H1': -0.85, 'H2': 0.2, 'NCI': 0.049211, 'P1': 10.5, 'P2': 0.180, 'SASA': 1.932, 'V': 80.7},
'R': {'H1': -2.53, 'H2': 3.0, 'NCI': 0.043587, 'P1': 10.5, 'P2': 0.291, 'SASA': 2.560, 'V': 105.0},
'S': {'H1': -0.18, 'H2': 0.3, 'NCI': 0.004627, 'P1': 9.2, 'P2': 0.062, 'SASA': 1.298, 'V': 29.3},
'T': {'H1': -0.05, 'H2': -0.4, 'NCI': 0.003352, 'P1': 8.6, 'P2': 0.108, 'SASA': 1.525, 'V': 51.3},
'V': {'H1': 1.08, 'H2': -1.5, 'NCI': 0.057004, 'P1': 5.9, 'P2': 0.140, 'SASA': 1.645, 'V': 71.5},
'W': {'H1': 0.81, 'H2': -3.4, 'NCI': 0.037977, 'P1': 5.4, 'P2': 0.409, 'SASA': 2.663, 'V': 145.5},
'Y': {'H1': 0.26, 'H2': -2.3, 'NCI': 117.3000, 'P1': 6.2, 'P2': 0.298, 'SASA': 2.368, 'V': 0.023599},
}

AAC = {
'1': ['A', 'G', 'V'],
'2': ['I', 'L', 'F', 'P'],
'3': ['Y', 'M', 'T', 'S'],
'4': ['H', 'N', 'Q', 'W'],
'5': ['R', 'K'],
'6': ['D', 'E'],
'7': ['C']
}

def _avg_sd(NUMBERS):
    AVG = sum(NUMBERS) / len(NUMBERS)
    TEM = [pow(NUMBER - AVG, 2) for NUMBER in NUMBERS]
    DEV = sum(TEM) / len(TEM)
    SD = math.sqrt(DEV)
    return (AVG, SD)

# PCPVS: Physicochemical property values
PCPVS = {'H1': [], 'H2': [], 'NCI': [], 'P1': [], 'P2': [], 'SASA': [], 'V': []}
for AA, PCPS in AAPCPVS.items():
    for PCPN in PCPNS:
        PCPVS[PCPN].append(PCPS[PCPN])

# PCPASDS: Physicochemical property avg and sds
PCPASDS = {}
for PCP, VS in PCPVS.items():
    PCPASDS[PCP] = _avg_sd(VS)

# NORMALIZED_AAPCPVS
NORMALIZED_AAPCPVS = {}
for AA, PCPS in AAPCPVS.items():
    NORMALIZED_PCPVS = {}
    for PCP, V in PCPS.items():
        NORMALIZED_PCPVS[PCP] = (V - PCPASDS[PCP][0]) / PCPASDS[PCP][1]
    NORMALIZED_AAPCPVS[AA] = NORMALIZED_PCPVS

def _pcp_value_of(AA, PCP):
    """Get physicochemical properties value of amino acid."""
    return NORMALIZED_AAPCPVS[AA][PCP];

def _pcp_sequence_of(PS, PCP):
    """Make physicochemical properties sequence of protein sequence."""
    PCPS = []
    for I, CH in enumerate(PS):
        PCPS.append(_pcp_value_of(CH, PCP))
    # Centralization
    AVG = sum(PCPS) / len(PCPS)
    for I, PCP in enumerate(PCPS):
        PCPS[I] = PCP - AVG
    return PCPS

def _ac_values_of(PS, PCP, LAG):
    """Get ac values of protein sequence."""
    AVS = []
    PCPS = _pcp_sequence_of(PS, PCP)
    for LG in range(1, LAG + 1):
        SUM = 0
        for I in range(len(PCPS) - LG):
            SUM = SUM + PCPS[I] * PCPS[I + LG]
        SUM = SUM / (len(PCPS) - LG)
        AVS.append(SUM)
    return AVS

def _all_ac_values_of(PS, LAG):
    """Get all ac values of protein sequence."""
    AAVS = []
    for PCP in PCPS:
        AVS = _ac_values_of(PS, PCP, LAG)
        AAVS = AAVS + AVS
    return AAVS

def _ac_code_of(PS):
    """Get ac code of protein sequence."""
    AC_Code = _all_ac_values_of(PS, 30)
    # Normalizing AC_Code
    # MIN_CODE = min(AC_Code)
    # MAX_CODE = max(AC_Code)
    # AC_Code = [(N-MIN_CODE)*1.0/(MAX_CODE-MIN_CODE) for N in AC_Code]
    return AC_Code

# CT CODE

# AAC_R: Reverse of AAC.
AAC_R = {}
for C, AAS in AAC.items():
    for AA in AAS:
        AAC_R[AA] = C

def _classification_of(AA):
    """Get classification of amino acids."""
    return AAC_R[AA]

def _classification_sequence_of(PS):
    """Make classification sequence from protein sequence."""
    CS = ''
    for I, CH in enumerate(PS):
        CS = CS + _classification_of(CH)
    return CS

def _ct_code_of(PS):
    """Get CT Code of protein sequence."""
    CT_Code = [0] * 343
    CS = _classification_sequence_of(PS)
    for I in range(len(CS) - 2):
        SubCS = CS[I:I + 3]
        CT_Code_Index = int(SubCS[0]) + (int(SubCS[1]) - 1) * 7 + (int(SubCS[2]) - 1) * 7 * 7
        CT_Code[CT_Code_Index - 1] = CT_Code[CT_Code_Index - 1] + 1
    SUM = sum(CT_Code)
    CT_Code = [N * 1.0 / SUM for N in CT_Code]
    # Normalizing CT_Code
    # MIN_CODE = min(CT_Code)
    # MAX_CODE = max(CT_Code)
    # CT_Code = [(N-MIN_CODE)*1.0/(MAX_CODE-MIN_CODE) for N in CT_Code]
    return CT_Code

# LD Code
def _ld_info_of(CS):
    L = len(CS)
    C = {}
    T = {}
    for I, CH in enumerate(CS):
        if CH not in C:
            C[CH] = []
        C[CH].append(I + 1)
        if I > 0:
            PCH = CS[I - 1]
            if PCH != CH:
                if int(PCH) < int(CH):
                    TIndex = PCH + CH
                else:
                    TIndex = CH + PCH
                if TIndex not in T:
                    T[TIndex] = 0
                T[TIndex] = T[TIndex] + 1
    return L, C, T

def _ld_code_of_0(CS):
    RC = [0] * 7
    RT = [0] * 21
    RD = [0] * 35
    L, C, T = _ld_info_of(CS)
    for Class, Indexs in C.items():
        Len = len(Indexs)
        RC[int(Class) - 1] = Len * 1.0 / L
        Residues = [1, int(Len * 0.25), int(Len * 0.5), int(Len * 0.75), Len]
        # Residues = list(map(lambda x:x*1.0/L, Residues))
        Residues = list(map(lambda x: Indexs[x - 1] * 1.0 / L, Residues))
        RD[(int(Class) - 1) * 5:int(Class) * 5] = Residues
    for Trans, Frequency in T.items():
        PI, I = int(Trans[0]) - 1, int(Trans[1]) - 1
        Index = int((21 - (6 - PI) * (6 - PI + 1) / 2) + (I - PI - 1))
        RT[Index] = Frequency * 1.0 / (L - 1)
    # return RC, RT, RD
    return RC + RT + RD

def _ld_code_of(PS):
    """Get LD Code of protein sequence."""
    CS = _classification_sequence_of(PS)
    L = len(CS)
    A = _ld_code_of_0(CS[0:int(L * 0.25)])
    B = _ld_code_of_0(CS[int(L * 0.25):int(L * 0.50)])
    C = _ld_code_of_0(CS[int(L * 0.50):int(L * 0.75)])
    D = _ld_code_of_0(CS[int(L * 0.75):L])
    E = _ld_code_of_0(CS[0:int(L * 0.50)])
    F = _ld_code_of_0(CS[int(L * 0.50):L])
    G = _ld_code_of_0(CS[int(L * 0.25):int(L * 0.75)])
    H = _ld_code_of_0(CS[0:int(L * 0.75)])
    I = _ld_code_of_0(CS[int(L * 0.25):L])
    J = _ld_code_of_0(CS[int(L * 0.125):int(L * 0.875)])
    return A + B + C + D + E + F + G + H + I + J

def _numbers_to_str(NUMBERS):
    return ' '.join([str(NUMBER) for NUMBER in NUMBERS])

def _generate_ac_code(arr):
    ac_coded = np.array([])
    for i in range(len(arr)):
        result = _numbers_to_str(_ac_code_of(arr[i][0]) + _ac_code_of(arr[i][1]))
        ac_coded = np.append(ac_coded, result)
    return ac_coded

def _generate_ct_code(arr):
    ct_coded = np.array([])
    for i in range(len(arr)):
        result = _numbers_to_str(_ct_code_of(arr[i][0]) + _ct_code_of(arr[i][1]))
        ct_coded = np.append(ct_coded, result)
    return ct_coded

def _generate_ld_code(arr):
    ld_coded = np.array([])
    for i in range(len(arr)):
        result = _numbers_to_str(_ld_code_of(arr[i][0]) + _ld_code_of(arr[i][1]))
        ld_coded = np.append(ld_coded, result)
    return ld_coded

def _prediction(arr, x):
    ac_coded = _generate_ac_code(arr)
    ct_coded = _generate_ct_code(arr)
    ld_coded = _generate_ld_code(arr)
    
    this_dir, this_filename = os.path.split(__file__)  # Get path of *.pkl
    model_path_ac = os.path.join(this_dir, 'rf_ac_1.pkl')
    model_path_ct = os.path.join(this_dir, 'rf_ct_1.pkl')
    model_path_ld = os.path.join(this_dir, 'rf_ld_1.pkl')
    loaded_model_ac = pickle.load(open(model_path_ac, 'rb'))
    loaded_model_ct = pickle.load(open(model_path_ct, 'rb'))
    loaded_model_ld = pickle.load(open(model_path_ld, 'rb'))
 
    data_ac = np.empty((0, 420), float)
    for i in range(len(ac_coded)):
        data_ac = np.append(data_ac, np.array([ac_coded[i].split(" ")]), axis=0)

    data_ct = np.empty((0, 686), float)
    for i in range(len(ct_coded)):
        data_ct = np.append(data_ct, np.array([ct_coded[i].split(" ")]), axis=0)

    data_ld = np.empty((0, 1260), float)
    for i in range(len(ld_coded)):
        data_ld = np.append(data_ld, np.array([ld_coded[i].split(" ")]), axis=0)

    ans_ac = loaded_model_ac.predict(data_ac)
    ans_ct = loaded_model_ct.predict(data_ct)
    ans_ld = loaded_model_ld.predict(data_ld)
    result_ac = loaded_model_ac.predict_proba(data_ac)
    result_ct = loaded_model_ct.predict_proba(data_ct)
    result_ld = loaded_model_ld.predict_proba(data_ld) 
    if x==0:
        return ans_ac, ans_ct, ans_ld, len(data_ac)
    elif x==1:
        return result_ac, result_ct, result_ld, len(data_ac)
    else:
        return ans_ac, ans_ct, ans_ld, result_ac, result_ct, result_ld, len(data_ac)
    

def predict(arr):
    """This function predicts the interaction between the given pairs of protein. '1' indicates 'Interaction'
    and '0' indicates 'No Interaction' between the pairs """
    print("Predicting...")
    result_ac, result_ct, result_ld, x = _prediction(arr, 0)
    result = np.array([])
    for i in range(x):
        l = [result_ac[i], result_ct[i], result_ld[i]]
        result = np.append(result, mode(l))
    
    print("Completed.")
    return result

def predict_proba(arr):
    """This function predicts the class probabilities, i.e., the probability of 'No Interaction'
       and probability of 'Interaction'. The sum of class probabilities will always be equal to 1."""
    print("Predicting probability...!!!")
    result_ac, result_ct, result_ld, x = _prediction(arr, 1)
    result = np.empty((x, 2), float)
    for i in range(x):
        result[i][0] = (result_ac[i][0] + result_ct[i][0] + result_ld[i][0]) / 3
        result[i][1] = (result_ac[i][1] + result_ct[i][1] + result_ld[i][1]) / 3
    
    print("Completed.")
    return result

def gen_file(arr):
    """This function generates the output file in .txt format."""
    ans_ac, ans_ct, ans_ld, result_ac, result_ct, result_ld, x = _prediction(arr, 5)
    ans = np.array([])
    result = np.empty((x, 2), float)
    for i in range(x):
        l = [ans_ac[i], ans_ct[i], ans_ld[i]]
        ans = np.append(ans, mode(l))
        result[i][0] = (result_ac[i][0] + result_ct[i][0] + result_ld[i][0]) / 3
        result[i][1] = (result_ac[i][1] + result_ct[i][1] + result_ld[i][1]) / 3
    result_file = "output.txt"
    output = open(result_file, 'w')
    output.write("S.No." + ' ')
    output.write("ACR Protein(s)" + ' ')
    output.write("CAS Protein(s)" + ' ')
    output.write("Probability_of_No_Interaction" + ' ')
    output.write("Probability_of_Interaction" + ' ')
    output.write("Prediction" + '\n')
    res = int(''.join(map(str, ans.shape)))
    for i in range(res):
        output.write(str(i + 1) + ' ')
        output.write(arr[i][0] + ' ')
        output.write(arr[i][1] + ' ')
        output.write(str(round(result[i][0], 5)) + ' ')
        output.write(str(round(result[i][1], 5)) + ' ')
        output.write(str(int(ans[i])) + '\n')
    output.close()
    print("File generated successfully!")
    return "File Generated Successfully!"