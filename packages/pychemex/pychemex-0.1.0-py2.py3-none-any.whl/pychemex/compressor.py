# Compressor class to simulate compressors, discharge temperture and work required will be calculated
from UNITS.stream import Stream
import copy, math

class Compressor:
    def __init__(self, name: str, stream: Stream, discharge_pres = None, pres_ratio = None, isentropic = True, allowable_moisture = 0.02):
        """
        Compressor class takes a stream and performs isentropic or polytropic calculations for given compression specifications
        -------------------------------------
        PARAMETERS
        name: (str) name of the unit (for identification)
        stream: Stream class instance specifying the fluid
        Optional discharge_pres(Pa): discharge pressure
        Optional pressure_ratio: ratio of discharge to suction pressure
        * Either pressure ratio or discharge pressure has to be specified
        Optional isentropic (boolean): True if compression is to be assumed isentropic, false for polytropic compression
        Optional allowable_moisture (fraction): fraction of maximum moisture content allowed in the feed (default is 2%)
        ----------------------------------------
        ATTRIBUTES
        name: name of unit
        feed: stream class instance representing feed for the compressor
        discharge: stream class instance representing discharge conditions
        isentropic: True or False depending on isentropic/polytropic requirement
        work: work required by the compressor for given discharge specification
        pres_ratio: ratio of discharge to suction pressure
        """
        self.name = name
        self.feed = stream
        if discharge_pres is None:  # check pressure ratio
            if pres_ratio is None:  # throw an error
                raise ValueError(f"Invalid discharge specifications for compressor {self.name}")
            else:
                self.pres_ratio = pres_ratio
        else:
            if pres_ratio is not None:  # both outlet pressure and pressure ratio are specified, system is over-specified
                raise ValueError(f"Invalid discharge specifications for compressor {self.name}, system is over-specified")
            else:
                self.pres_ratio = discharge_pres/self.feed.pres
        if self.feed.material.flash(P=self.feed.pres, T=self.feed.temp, zs = self.feed.composition).VF < (1-allowable_moisture):
            print(f"moisture content in compressor feed is greater than maximum allowable limit of {allowable_moisture*100}%\nCalculations cannot proceed")
            raise Exception("too much moisture in the feed (you can change the moisture content in initialisation")
        self.isentropic = isentropic
        print(f"Feed specification for compressor {self.name}")
        self.feed.show()
        self.discharge = self.discharge_stream()
        # print(f"Discharge stream for compressor {self.name}")
        # self.discharge.show()
        # self.work = self.work()
    
    def isentropic_temp(self):
        """
        calculates discharge temperature for isentropic compression
        """
        feed_entropy = self.feed.material.flash(T=self.feed.temp, P=self.feed.pres, zs = self.feed.composition).gas.S()
        discharge_pres = self.feed.pres*self.pres_ratio
        discharge_flash = self.feed.material.flash(S=feed_entropy, P=discharge_pres, zs = self.feed.composition)
        return discharge_flash.T

    def polytropic_temp(self):
        """
        discharge temperature for polytropic compression
        """
        discharge_pres = self.feed.pres*self.pres_ratio
        density = self.feed.material.flash(T=self.feed.temp, P=self.feed.pres, zs = self.feed.composition).gas.rho_mass()
        # density in kg/m^3
        gamma = self.feed.cpcv_gas()    # cp/cv ratio for the given mixture
        mass_flow = self.feed.mass_flow()       # kg/s
        eff_poly = 0.61 + (0.03 * math.log(0.5885*mass_flow*3600/density))
        n_ratio = (gamma/(gamma-1))*eff_poly        # n/n-1
        discharge_temp = self.feed.temp*((self.pres_ratio)**(1/n_ratio))
        return discharge_temp
    
    def discharge_stream(self):
        # calculates the discharge stream conditions (feed stream with pressure and temperature updated)
        if self.isentropic:
            discharge_temp = self.isentropic_temp()
        else:
            discharge_temp = self.polytropic_temp()
        discharge = copy.deepcopy(self.feed)
        discharge.temp = discharge_temp
        discharge.pres = self.pres_ratio * self.feed.pres
        return discharge
    def work(self):
        """
        calculate the power required for compression (J/s = Power)
        Calculations are done considering only the gas phase
        """
        # handling bug for near critical phase error
        # this is just a bypass and will need a fix
        try:        
            enthalpy_in = self.feed.material.flash(T=self.feed.temp, P=self.feed.pres, zs = self.feed.composition).gas.H()
        except:
            enthalpy_in = self.feed.material.flash(T=self.feed.temp, P=self.feed.pres, zs = self.feed.composition).H()
        try:
            enthalpy_out =  self.discharge.material.flash(T=self.discharge.temp, P=self.discharge.pres, zs = self.discharge.composition).gas.H()
        except:
            enthalpy_out =  self.discharge.material.flash(T=self.discharge.temp, P=self.discharge.pres, zs = self.discharge.composition).H()
        specific_work = enthalpy_out - enthalpy_in       # J/mol
        return specific_work * self.feed.molar_flow      # W

    # multistage compression
    def multistage(self, nstages, maximum_feed_temp, after_cooler=True, utility=None, utility_discharge_temp=None, intermediate_values = False):
        """
        splits the single unit into multistage compression with interstage coolers
        PARAMETERS
        nstages (INT): number of stages desired for compression
        maximum_feed_temp (Float) K: maximum allowable feed temperature of feed gases for each stage
        
        OPTIONAL utility (Stream): stream class object, defining cooling stream specifications
        OPTIONAL utility_discharge_temp (K): discharge temperature for utility stream
        OPTIONAL after_cooler(boolean): whether interstage cooler is extended to the end of final stage or not
        * if utility is specified, discharge temperature must also be specified for flow rate calculations
        ** flow rate of utility stream will be reported for each stage if specified
        -------------------------------------------------
        RETURNS
        Dictionary containing following data for each stage
        work required(list);
        discharge temperature(list);
        cooling duty(list);
        utility flow rate(list);
        final discharge stream(Stream class object)  
        """
        if utility is not None and utility_discharge_temp is None:
            raise ValueError("Value for utility discharge temperature must be specified if utility is specified")
        
        stage_ratio = self.pres_ratio**(1/nstages)
        discharge_pres = self.feed.pres*self.pres_ratio
        condition = self.isentropic
        self.pres_ratio = stage_ratio
        works = []
        discharge_temps = []
        cooling_duties = []
        if utility is None: # no utility usage
            utility_usage = None
        else:   # use container for utility usage
            utility_usage = []
        # check and cool down initial feed if necessary
        if self.feed.temp > maximum_feed_temp:
            print("reducing feed temp")
            (self.feed, feed_duty) = self.feed.update_temp(maximum_feed_temp)
            cooling_duties.append(feed_duty)
        i = 0
        for i in range(nstages):
                if intermediate_values == True:
                    print(f"-------Feed at Stage {i + 1}-------------")
                    self.feed.show()
                stage_discharge = self.discharge_stream()
                if intermediate_values == True:
                    print(f"-------Discharge at Stage {i + 1}-------------")
                    stage_discharge.show()
                discharge_temps.append(stage_discharge.temp)
                works.append(self.work)
                if stage_discharge.temp > maximum_feed_temp:    # cooling is required
                    (self.feed, stage_duty) = stage_discharge.update_temp(maximum_feed_temp)
                    cooling_duties.append(stage_duty)
                if utility is not None:    
                    # report utility flow rate required for this stage
                    utility_usage.append(utility.calculate_utility(utility_discharge_temp, stage_duty))
                else:   # no cooling required
                    self.feed = stage_discharge
                    cooling_duties.append(0.)
                if utility is not None:
                    # append zero for this stage
                    utility_usage.append(0.)
        utility_usage.pop()
        cooling_duties.pop()
        # if after cooler is installed, re-evaluate final stream
        if after_cooler and stage_discharge.temp > maximum_feed_temp:
            (updated_discharge, discharge_duty) = stage_discharge.update_temp(maximum_feed_temp)
            cooling_duties.append(discharge_duty)
            if utility is not None:
                utility_usage.append(utility.calculate_utility(utility_discharge_temp, discharge_duty))
            self.discharge = updated_discharge
        else:
            self.discharge = stage_discharge
            if after_cooler:
                utility_usage.append(0.)
        
        print("=="*20)
        print(f"Discharge results from final compression stage of {self.name}")
        self.discharge.show()
        unit = {
            "stage work": works,
            "stage discharge temps": discharge_temps,
            "stage cooling duties": cooling_duties,
            "stage utility requirement": utility_usage,
            "final discharge":self.discharge
        }
        return unit


