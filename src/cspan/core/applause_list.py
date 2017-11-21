class ApplauseList:
	def __init__(self, file_path):
		self.applause_times_file = file_path
						
	def get_applause_times(self, f):
		lines = [l.rstrip() for l in open(f).read().split('\n')]
		applause_count = int(lines[0].split(": ")[1])
		total_applause_time = float(lines[1].split(": ")[1])
		applause_times = [tuple([float(l.rstrip()) for l in line.split('\t')]) for line in lines[2:-1]]
		return (applause_count, total_applause_time, applause_times)
		
	def combine_instances(self, instances):
		pointer = 0
		while(pointer < len(instances)-1):
			start_time = instances[pointer][0]; end_time = instances[pointer][1]
			next_start_time = instances[pointer+1][0]; next_end_time = instances[pointer+1][1]
			if((next_start_time - end_time) < 0.2):
				instances[pointer] = (start_time,next_end_time)
				instances.pop(pointer+1)
			else:
				pointer += 1
		return instances		
				
	def get_instances(self):
		applause_count, total_applause_time, instances = self.get_applause_times(self.applause_times_file)
		self.combine_instances(instances)
		instances = [i for i in instances if i[1]-i[0] > 2]
		return instances
