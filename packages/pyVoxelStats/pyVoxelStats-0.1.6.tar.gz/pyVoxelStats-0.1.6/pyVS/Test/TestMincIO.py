import tempfile
import pyminc.volumes.factory as fc
import pyVS
try:
    data_path = pyVS.get_data('I34.mnc')
    h1 = fc.volumeFromFile(data_path)
    h1.closeVolume()
    h = fc.volumeLikeFile(data_path, '{0}/test.mnc'.format(tempfile.gettempdir()))
    h.closeVolume()
    print('MINC IO test successfull. ')
except Exception as e:
    print('Error in MINC IO. MINC file operations may fail. PLease make sure if you have installed latest minc-toolkit and sourced it. ')
    print(e)
