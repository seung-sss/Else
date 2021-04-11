subroutine gauss_filter(img, h, w, blurImg)
	integer, intent(in) :: h, w
	integer, intent(in) :: img(h,w,3)
	integer, intent(out) :: blurImg(h-2,w-2,3)
	integer :: gauss(9), summ
	gauss(1) = 1
	gauss(2) = 2
	gauss(3) = 1
	gauss(4) = 2
	gauss(5) = 4
	gauss(6) = 2
	gauss(7) = 1
	gauss(8) = 2
	gauss(9) = 1

	do k = 1,3
		do i = 2, h-1
			do j= 2, w-1
				l = 1
				summ = 0
				do ii = -1, 1
					do jj = -1, 1
						summ = summ + img(i+ii, j+jj, k)*gauss(l)
						l = l + 1
					end do
				end do
				blurImg(i-1,j-1,k) = summ / 16
			end do
		end do
	end do
	return
end subroutine

subroutine med_filter(img, h, w, blurImg)
	integer, intent(in) :: h, w
	integer, intent(in) :: img(h,w,3)
	integer, intent(out) :: blurImg(h-2,w-2,3)
	integer :: temp(9)
	
	do k = 1, 3
		do i = 2, h-1
			do j= 2, w-1
				l = 1
				do ii = -1, 1
					do jj = -1, 1
						temp(l) = img(i+ii, j+jj, k)
						l = l + 1
					end do
				end do
				blurImg(i-1, j-1, k) = median(temp)
			end do
		end do
	end do
	return
end subroutine
							
integer function median(arr)
	integer, intent(in) :: arr(9)
	integer :: sort_arr(9), tmp
	sort_arr(1) = arr(1)
	sort_arr(2) = arr(2)
	sort_arr(3) = arr(3)
	sort_arr(4) = arr(4)
	sort_arr(5) = arr(5)
	sort_arr(6) = arr(6)
	sort_arr(7) = arr(7)
	sort_arr(8) = arr(8)
	sort_arr(9) = arr(9)
	
	do i = 1, 9
		do j = 2, 9
			if (sort_arr(j) .LT. sort_arr(j-1)) then
				tmp = sort_arr(j)
				sort_arr(j) = sort_arr(j-1)
				sort_arr(j-1) = tmp
			end if
		end do
	end do
	median = sort_arr(5)
end function

subroutine rotate(img, h, w, rad, rotateImg)
	integer, intent(in) :: h, w
	real, intent(in) :: rad
	integer, intent(in) :: img(h,w,3)
	integer, intent(out) :: rotateImg(h,w,3)
	integer :: x, y, x0, y0
	
	x0 = h / 2
	y0 = w / 2
	
	do k = 1, 3
		do i = 1, h
			do j= 1, w
				x = INT((i - x0) * COS(rad) - (j - y0) * SIN(rad) + x0)
				y = INT((i - x0) * SIN(rad) + (j - y0) * COS(rad) + y0)
				if (x .LT. h .and. x .GE. 0) then
					if (y .LT. w .and. y .GE. 0) then
						rotateImg(x, y, k) = img(i, j, k)
					end if
				end if
			end do
		end do
	end do
	return
end subroutine
	
	