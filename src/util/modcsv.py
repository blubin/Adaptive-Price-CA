# Copyright (c) 2023 Benjamin Lubin and Sebastien Lahaie.
#
# This file is part of Adaptive-Price-CA
# (see https://github.com/blubin/Adaptive-Price-CA).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""
An enhancement to the built-in csv.dictwriter so it can add
columns on the fly.

(c) Benjamin Lubin 11/17/19
"""

from csv import DictWriter
import mmap, os

class ModifiableDictWriter(DictWriter):

  def __init__(self, f, fieldnames=[], restval='', extrasaction='auto',
               dialect='excel', *args, **kwds):
    """ Note: you must write a header (but it can be empty).
        Note2: when you call writerow(dict) you might want to use
               an OrderedDict if you want to be sure the headers appear
               in order.
    """
    DictWriter.__init__(self, f, fieldnames, restval,
                        'raise', dialect,
                        *args, **kwds)
    if extrasaction.lower() not in ("raise", "ignore", "auto"):
      raise ValueError("extrasaction (%s) must be 'raise','ignore' or 'auto'"
                       % extrasaction)
    self.extrasaction = extrasaction # set this ourselves, to allow for
                                     # new setting 'auto'
    self.mmfile = ModifieableMappedFile(f)

  def addheader(self, header):
    """ Add a header to the existing csv file.
        extrasaction specifies what to do if the header already exists:
        ignore|raise
    """
    if header in self.fieldnames:
      if extrasaction.lower()=='raise':
        raise ValueError("CSV already contains header (%s)." % header)
      else:
        return
    if len(self.fieldnames) > 0:
      self.mmfile.insert_all(os.linesep, ',', location="before")
    self.fieldnames.append(header)
    self.mmfile.insert(self.mmfile.find(os.linesep)-1, header)
    self.mmfile.close()

  def _dict_to_list(self, rowdict):
    """ override internal method, so we auto create headers if we 
        are supposed to.
    """
    if self.extrasaction == 'auto':
      wrong_fields = set(rowdict.keys()) - set(self.fieldnames)
      for field in wrong_fields:
        self.addheader(field)
    return DictWriter._dict_to_list(self, rowdict)
    
class ModifieableMappedFile:
  """ Wrapper around mmap that lets us do modifications. 
      file should be maintained with pointer at end.
  """
  def __init__(self, file):
    self.file = file
    self._mm = None

  @property
  def mm(self):
    """ get the mmap """
    if not self._mm:
      self._mm = mmap.mmap(self.file.fileno(), 0)
    return self._mm

  def close(self):
    if self._mm:
      self._mm.close()
      self._mm=None

  def find(self, string, start=None, end=None):
    """ find the location of string in the file, return -1 if not found """
    self.file.flush()
    if start and end:
      return self.mm.find(string, start, end)
    elif start:
      return self.mm.find(string, start)
    else:
      return self.mm.find(string)
      
  def insert(self, loc, content):
    """ insert content into file at given location"""
    self.file.flush()                                    # be sure to flush
    self.file.seek(0,2)                                  # goto end
    size = self.file.tell()                              # get size
    self.file.write(b"\0" * len(content))                  # grow file
    self.file.flush()
    self.close()                                         # ensure open again
    self.mm.move(loc+len(content),loc,size-loc)          # move file forward
    self.mm[loc:loc+len(content)]=content                # insert content
    self.mm.flush()                                      # flush the file
    self.file.seek(0,2)                                  # goto new end

  def insert_all(self, search, insertion, location="before"):
    """ Find all instances of search, and insert the given string 
        either before or after depending on location arg.
    """
    offset = -1 if location.lower()=="before" else len(search)-1
    loc = self.find(search)
    while loc != -1:
      self.insert(loc+offset, insertion)
      #print "|"+repr(self._mm[:])+"|"
      loc = self.find(search, loc+len(search)+len(insertion))

    
if __name__ == "__main__":
  with open('test1.csv', 'w+') as f:
    csv = ModifiableDictWriter(f)
    csv.writeheader()
    csv.writerow({'A':'1','B':'2'})
    csv.writerow({'A':'3','B':'4','C':'5'})
    csv.writerow({'A':'6','B':'7','C':'8', 'D':'9'})

  with open('test2.csv', 'w+') as f:
    csv = ModifiableDictWriter(f, ['A', 'B'])
    csv.writeheader()
    csv.writerow({'A':'1','B':'2'})
    #csv.addheader('C')
    csv.writerow({'A':'3','B':'4','C':'5'})
    csv.writerow({'A':'6','B':'7','C':'8', 'D':'9'})
  print 'Done.'
