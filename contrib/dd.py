from sets import Set

class DB:
	db = []
	
	def add(self,param_dict,data_name,data):
	    if not self.exist(param_dict,data_name):
	    	self.db.append((param_dict,data_name,data))
	    else:
		print "Data point exists: ", param_dict , ":::" , data_name  

	def load_db(self,filename):
 	    f = open(filename,'rb')
            import pickle
            self.db = pickle.load(f)

	def save_db(self,filename):
 	    f = open(filename,'wb')
            import pickle
            pickle.dump(self.db,f)
	
	def exist(self,params,data_name):
            for (d,dn,t) in self.db:		
    		
	    	if len(params.keys()) != len(d.keys()):
 		   continue
		f = True  
		for k in d.keys():
		    if k not in params:
		       f = False
		       break;
		    if d[k] != params[k]:
		       f = False
		       break
		if f and (data_name == dn):
		   return True
		
	    return False  		
		
	
	def find(self,params,data_name=None):
		
		matches = []
		idd = 0
		for d in self.db:
		    idd+=1
		    match = True;
		    for p in params.keys():
			if d[0].has_key(p) and (d[0][p] == params[p]):
			   continue
			else:
			   match = False;
			   			
		    if match and ((data_name == None) or (data_name == d[1])):
		       (a,b,c) = d
		       matches.append((a,b,c,idd-1))
		   
		   
	    	return matches
		    
		    
		    
		    

class DB2:
	
	def __init__(self,parent):
    	    self.children_params = []
	    self.children = []
	    self.data = {}
   	    self.register = []
	    
	    self.parent=parent
	    self.idd = self.register_yourself(self)
	    
	    
	def register_yourself(self,who):
	    if self.parent != None: return self.parent.register_yourself(who)
	    self.register.append(who)
	    return len(self.register)-1

		
	
	def get_child(self,param_dict):
	    for (cp,c) in zip(self.children_params,self.children):
	        if Set(param_dict.keys()) != Set(cp.keys()):
		   continue
		eq=True
		for k in cp.keys():
		    if cp[k] != param_dict[k]:
		       eq=False
	        if eq:
		   return c
	    self.children_params.append(param_dict)
	    new_node = DB2(self)
	    self.children.append(new_node)
	    return new_node	
		
	def add_data(self,data_name,data,force=False):
	    if data_name in self.data.keys():
	       if force:	     
	       	  print "TRYING TO OVERWRITE DATA: ", data_name, " ALLOWING"
		  self.data[data_name] = data 
	       else:
		  print "TRYING TO OVERWRITE DATA: ", data_name, "NOT ALLOWING"
	    self.data[data_name] = data	
	
	def get_data(self,data_name):
	    if data_name in self.data.keys():
	       return self.data[data_name]
	    print "DATA DOES NOT EXIST:", data_name
	    return None 	
