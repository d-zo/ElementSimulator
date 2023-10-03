program Stresspath_test
   use Preparation, only: Get_Material, Prepare_State, Postprocess_State
   implicit none

   ! IMPORTANT: UMAT allows single AND double precision, but some implementations require double precision
   integer, parameter :: dp = selected_real_kind(15)
   !
   integer, parameter :: ndi = 3
   integer, parameter :: nshr = 3
   integer, parameter :: ntens = 6
   integer, parameter :: nstatv = 20
   integer, parameter :: nprops = --numparameter--
   real(dp), dimension(ntens) :: ddsddt, drplde, stran
   real(dp), dimension(ntens, ntens) :: ddsdde
   real(dp), dimension(3, 3) :: drot, dfgrd0, dfgrd1
   real(dp), dimension(3) :: coords
   real(dp), dimension(2) :: time
   real(dp), dimension(1) :: predef, dpred
   real(dp) :: sse, spd, scd, rpl, drpldt, temp, dtemp, celent, pnewdt
   integer, dimension(4) :: jstep
   integer :: noel, npt, layer, kspt, kinc
   !
   character(len=80) :: materialname, check_materialname
   character(len=40) :: material_description
   real(dp), dimension(16) :: materialparam_vec
   real(dp), dimension(nprops) :: materialparameters
   real(dp), dimension(nstatv) :: statevariables, inoutstate
   real(dp), dimension(ntens) :: inoutstress, inpstrain
   real(dp), dimension(6) :: intergranular_strain
   real(dp), dimension(6) :: pressure_origin
   real(dp), dimension(2) :: minmax_stress
   integer, parameter :: num_angles = --spider_numangles--
   real(dp), parameter :: refstrain = --spider_refstrain--
   real(dp) :: dt, initial_voidratio, voidratio, angle, ref_intergranular_strain
   integer :: idx, filenr, stat, ixx, jxx, iangle
   integer, parameter :: maxiter = --maxiter--
   real(dp), parameter :: pi = 4.0_dp*atan(1.0_dp)
   real(dp), parameter :: isocomp_offset = atan(sqrt(2.0_dp))
   logical :: breakall, is_success, igran_active
   real(dp) :: starttime, endtime

   ddsddt = 0.0_dp
   drplde = 0.0_dp
   stran = 0.0_dp
   ddsdde = 0.0_dp
   drot = reshape([(1.0_dp, (0.0_dp, ixx = 1, 3), jxx = 1, 2), 1.0_dp], [3, 3])
   dfgrd0 = drot
   dfgrd1 = drot
   coords = 0.0_dp
   !
   predef = 0.0_dp
   dpred = 0.0_dp
   celent = 0.0_dp
   pnewdt = 0.0_dp
   sse = 0.0_dp
   spd = 0.0_dp
   scd = 0.0_dp
   rpl = 0.0_dp
   drpldt = 0.0_dp
   temp = 0.0_dp
   dtemp = 0.0_dp
   !
   jstep = 0
   noel = 0
   npt = 0
   layer = 0
   kspt = 0
   kinc = 0

   ! Decide which constitutive model to use by materialname
   check_materialname = '--materialname--'
   material_description = '--materialdescription--'
   igran_active = --igranactive--

   ! Time increment to be used
   time = [--starttime--, --starttime--]
   dt = --timeincrement--

   ! List material parameters to be used
   initial_voidratio = --initialvoidratio--
   voidratio = initial_voidratio
   intergranular_strain = [--intergranularstrain--]
   ref_intergranular_strain = intergranular_strain(2)

   ! State loads
   pressure_origin = [&
   --spider_refstress--]

   minmax_stress = [--spider_maxstress--]


   call Get_Material(material_description=material_description, igran_active=igran_active, &
      constitutive_model_name=check_materialname(1:9), adj_name=materialname, nu=0.25_dp, &
      materialparameters=materialparam_vec, success=is_success)
   if (.not. is_success) then
      stop 'Failed'
   end if
   materialparameters = materialparam_vec(1:nprops)

   call Prepare_State(constitutive_model_name=check_materialname(1:9), voidratio=voidratio, &
      intergranular_strain=intergranular_strain, igran_active=igran_active, integration_method=1, &
      first_dt=dt, integration_tolerance=0.0001_dp, statevariables=statevariables, success=is_success)
   if (.not. is_success) then
      stop 'Failed'
   end if


   filenr = 20
   open(filenr, file="--outfilename--.csv", iostat=stat)
   if (stat /= 0) then
      write(*, *) "Access problem during write attempt"
      close(filenr)
      stop
   end if


   breakall = .False.

   call cpu_time(starttime)
   stress_path: &
   do iangle = 1, num_angles
      inoutstress = pressure_origin
      voidratio = initial_voidratio

      angle = (real(iangle, dp) - 1.0_dp)/real(num_angles, dp)*2.0_dp*pi

      ! Add offset to start with isotropic compression
      inpstrain = refstrain*[ &
         cos(angle+isocomp_offset), sin(angle+isocomp_offset)/sqrt(2.0_dp), sin(angle+isocomp_offset)/sqrt(2.0_dp), &
         0.0_dp, 0.0_dp, 0.0_dp]*dt
      intergranular_strain = ref_intergranular_strain*[ &
         cos(angle+isocomp_offset), sin(angle+isocomp_offset)/sqrt(2.0_dp), sin(angle+isocomp_offset)/sqrt(2.0_dp), &
         0.0_dp, 0.0_dp, 0.0_dp]

      call Prepare_State(constitutive_model_name=check_materialname(1:9), voidratio=voidratio, &
         intergranular_strain=intergranular_strain, igran_active=igran_active, integration_method=1, &
         first_dt=dt, integration_tolerance=0.0001_dp, statevariables=inoutstate, success=is_success)

      time = --timeincrement--
      idx = 1

      ! Also save the first (starting) point each time
      write(filenr, '(i4, a, f13.6, a, f13.6, a, f13.6)') nint(angle*180.0_dp/pi), '   ', &
         -inoutstress(1), '   ', -inoutstress(2), '   ', voidratio

      loading_loop: &
      do
         if (any(inoutstress(1:3) < minmax_stress(1)) .or. any(inoutstress(1:3) > minmax_stress(2))) then
            exit loading_loop
         end if
         call UMAT(inoutstress, inoutstate, ddsdde, sse, spd, scd, rpl, ddsddt, drplde, drpldt, &
                   stran, inpstrain, time, dt, temp, dtemp, predef, dpred, materialname, ndi, nshr, &
                   ntens, nstatv, materialparameters, nprops, coords, drot, pnewdt, celent, dfgrd0, &
                   dfgrd1, noel, npt, layer, kspt, jstep, kinc)

         call Postprocess_State(constitutive_model_name=check_materialname(1:9), inoutstate=inoutstate, &
            nstates=nstatv, voidratio=voidratio, intergranular_strain=intergranular_strain, jacobian=ddsdde)

         write(filenr, '(i4, a, f13.6, a, f13.6, a, f13.6)') nint(angle*180.0_dp/pi), '   ', &
            -inoutstress(1), '   ', -inoutstress(2), '   ', voidratio

         ! No Assignment necessary: inoutstress and inoutstate are automatically reassigned in UMAT-call
         time = time + dt
         idx = idx + 1
         if (idx > maxiter) then
            write(*, *) 'Maximum number of specified iterations reached'
            breakall = .True.
            exit loading_loop
         end if
      end do loading_loop
      if (breakall) then
         exit stress_path
      end if
   end do stress_path
   call cpu_time(endtime)
   print '("--outfilename--: ",f6.3,"s")', endtime - starttime
   close(filenr)
end program Stresspath_test
