import numpy as np
import rospy

from controller import BaseController


class PIDController(BaseController):
    def __init__(self):
        super(PIDController, self).__init__()

        self.reset_params()
        self.reset_state()

    def get_reference_index(self, pose):
        '''
        get_reference_index finds the index i in the controller's path
            to compute the next control control against
        input:
            pose - current pose of the car, represented as [x, y, heading]
        output:
            i - referencence index
        '''
        with self.path_lock:
            # TODO: INSERT CODE HERE
            # Determine a strategy for selecting a reference point
            # in the path. One option is to find the nearest reference
            # point and chose the next point some distance away along
            # the path.

            # Note: this method must be computationally efficient
            # as it is running directly in the tight control loop.

            dis = np.zeros(len(self.path))
            for i in range(len(self.path)):
                dis[i] = np.sqrt((pose[0] - self.path[i][0])**2 + (pose[1] - self.path[i][1])**2)
            idx = np.argmin(dis)
            coord = self.path[idx, :2]


            index = idx
            for i in range(idx + 1, len(self.path)):
               if np.linalg.norm(self.path[i, :2] - coord) > self.waypoint_lookahead:
                    return i

            return index

    def get_control(self, pose, index):
        '''
        get_control - computes the control action given an index into the
            reference trajectory, and the current pose of the car.
            Note: the output velocity is given in the reference point.
        input:
            pose - the vehicle's current pose [x, y, heading]
            index - an integer corresponding to the reference index into the
                reference path to control against
        output:
            control - [velocity, steering angle]
        '''
        # TODO: INSERT CODE HERE
        # Compute the next control using the PD control strategy.
        # Consult the project report for details on how PD control
        # works.
        #
        # First, compute the cross track error. Then, using known
        # gains, generate the control.

        ref_pose = self.get_reference_pose(index)

        ep = self.get_error(pose, index)
        e_ct = ep[1]
        theta_e = pose[2] - ref_pose[2]
        V_e = ref_pose[3] * np.sin(theta_e)
        u = -(self.kp * e_ct + self.kd * V_e)

        return [ref_pose[3], u]
        # assert False, "Complete this function"

    def reset_state(self):
        '''
        Utility function for resetting internal states.
        '''
        with self.path_lock:
            pass

    def reset_params(self):
        '''
        Utility function for updating parameters which depend on the ros parameter
            server. Setting parameters, such as gains, can be useful for interative
            testing.
        '''
        with self.path_lock:
            self.kp = float(rospy.get_param("/pid/kp", 3)) # 0.8
            self.kd = float(rospy.get_param("/pid/kd", 1.5)) # 0.5
            self.finish_threshold = float(rospy.get_param("/pid/finish_threshold", 0.2)) # 0.2
            self.exceed_threshold = float(rospy.get_param("/pid/exceed_threshold", 4.0))
            # Average distance from the current reference pose to lookahead.
            self.waypoint_lookahead = float(rospy.get_param("/pid/waypoint_lookahead", 0.2))
