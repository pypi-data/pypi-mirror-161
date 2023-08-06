from sympy import symbols

t,t_1,t_2,t_3,y_1,y_2,y_3 = symbols("t,t_1,t_2,t_3,y_1,y_2,y_3")

p = (
		  (t-t_2)*(t-t_3)/(t_1-t_2)/(t_1-t_3)*y_1
		+ (t-t_1)*(t-t_3)/(t_2-t_1)/(t_2-t_3)*y_2
		+ (t-t_2)*(t-t_1)/(t_3-t_2)/(t_3-t_1)*y_3
	)

assert p.subs(t,t_1)==y_1
assert p.subs(t,t_2)==y_2
assert p.subs(t,t_3)==y_3

print(p.expand())
diff = p.diff(t).subs(t,t_2)
print(diff)

diff_2 = (
		  y_1*(t_2-t_3)/(t_2-t_1)/(t_3-t_1)
		+ y_2/(t_2-t_3)
		+ y_2/(t_2-t_1)
		+ y_3*(t_2-t_1)/(t_3-t_1)/(t_3-t_2)
	)

assert diff.equals(diff_2)
