from typing import List
import winreg

__version__ = "1.0.1"

class Path:
	"""Manipulating Windows environment(Path) variables"""

	SYSTEM_PATH_REG = r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
	USER_PATH_REG = r"Environment"

	def __init__(self, isSuperUser:bool=False) -> None:
		self.isSuperUser = isSuperUser

	def _getKeys(self):
		if self.isSuperUser:
			return (
				winreg.HKEY_LOCAL_MACHINE,
				self.SYSTEM_PATH_REG
			)
		else:
			return (
				winreg.HKEY_CURRENT_USER,
				self.USER_PATH_REG
			)

	def getPath(self) -> str:
		"""Gets the environment variable Path.

			@return	Environment variable path
		"""
		path = None
		with winreg.OpenKeyEx(*self._getKeys()) as key:
			path, _ = winreg.QueryValueEx(key, 'Path')
		return path


	def getPathList(self) -> List[str]:
		"""Get a list of Paths as a list

			@return	list of Paths
		"""
		return self.getPath().split(";")

	def setPath(self, path:str) -> None:
		"""Update Path.

			@param	path: String to be added to Path
			@return	None
		"""
		with winreg.CreateKeyEx(*self._getKeys()) as key:
			winreg.SetValueEx(key, 'Path', 0, winreg.REG_EXPAND_SZ, path)

	def addPath(self, path:str, priority:int=0) -> None:
		"""Adding non-overlapping paths.

			@param	path:	String to be added to Path.
							';' cannot be included.
			@return	None
		"""
		if ";" in path:
			raise ValueError("Do not specify more than one Path.")

		existPath: List[str] = self.getPathList()
		if path in existPath:
			existPath.remove(path)
		existPath.insert(priority, path)
		self.setPath(";".join(existPath))


	def removePath(self, path:str) -> None:
		"""Remove Path.
			@param	path	Target Path
		"""
		existPath: List[str] = self.getPathList()
		if ";" in path:
			raise ValueError("Do not specify more than one Path.")
		elif path not in existPath:
			raise ValueError("{} in Path".format(path))
		else:
			self.setPath(";".join([i for i in existPath if path != i]))




